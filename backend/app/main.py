import os
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
from models import Project as DBProject, Task as DBTask, Employee as DBEmployee, EmployeeTask, EmployeeProject 
from schemas import *
from auth import auth_router
from database import SessionLocal, engine, Base
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect
from jose import jwt, JWTError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from auth import verify_jwt


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if not tables:
            Base.metadata.create_all(bind=engine)
            print("Database and schema initialized successfully.")
        else:
            print("Database schema already exists.")
    except OperationalError as e:
        print("Database connection failed or schema is missing.")
        print(f"Error details: {str(e)}")
    
    yield
    print("Application shutting down.")



app = FastAPI(
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins="*", 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(auth_router)

SECRET_KEY = os.getenv("JWT_SECRET")  
ALGORITHM = "HS256"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/get-userdetails")
async def get_user_details(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token missing or invalid")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id = payload.get("employee_id")
        if employee_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=401, detail="Employee not found")
        
        return employee
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    

# Get all projects (ADMIN)
@app.get("/projects", response_model=ProjectListResponse)
async def get_projects(
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        projects = db.query(DBProject).all()

        project_list = []
        for project in projects:
            project_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == project.project_owner_id).first()
            if not project_owner:
                raise HTTPException(status_code=404, detail=f"Project owner with ID {project.project_owner_id} not found")

            managers = db.query(DBEmployee).join(EmployeeProject).filter(
                EmployeeProject.project_id == project.project_id, DBEmployee.role == "manager"
            ).all()

            members = db.query(DBEmployee).join(EmployeeProject).filter(
                EmployeeProject.project_id == project.project_id, DBEmployee.role == "member"
            ).all()

            project_list.append(ProjectResponse(
                project_id=project.project_id,
                project_name=project.name,
                description=project.description,
                start_date=project.start_date,
                end_date=project.end_date,
                project_status=project.project_status,
                project_owner_id=project.project_owner_id,
                project_owner_name=project_owner.name,
                managers=[{"employee_id" : manager.employee_id, "name" :manager.name} for manager in managers],
                members=[{"employee_id" : member.employee_id, "name" : member.name} for member in members],
            ))

        return ProjectListResponse(
            projects=project_list,
            project_count=len(projects)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Get project by id (ADMIN / MANAGER / EMPLOYEE)
@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(
    project_id: int, 
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)  
):

    if user.role != "admin" and user.role != "manager" and user.role != "member":
        raise HTTPException(status_code=403, detail="Access forbidden: Unauthorized User")

    try:
        project = db.query(DBProject).filter(DBProject.project_id == project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == project.project_owner_id).first()
        if not project_owner:
            raise HTTPException(status_code=404, detail="Project owner not found")

        managers = db.query(DBEmployee).join(EmployeeProject).filter(
            EmployeeProject.project_id == project.project_id, DBEmployee.role == "manager"
        ).all()

        members = db.query(DBEmployee).join(EmployeeProject).filter(
            EmployeeProject.project_id == project.project_id, DBEmployee.role == "member"
        ).all()

        return ProjectResponse(
            project_id=project.project_id,
            project_name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            project_status=project.project_status,
            project_owner_id=project.project_owner_id,
            project_owner_name=project_owner.name,
            managers=[{"employee_id" : manager.employee_id, "name" :manager.name} for manager in managers],
            members=[{"employee_id" : member.employee_id, "name" : member.name} for member in members],
        )

    except HTTPException as e:
        raise e  
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e



# Create a new project with assigned managers and employees (ADMIN)
@app.post("/projects", response_model=ProjectCreate)
async def create_project(
    project: ProjectBase,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "admin":
       raise HTTPException(status_code=403, detail="Access forbidden: Admins only")


    try:
        db_project = DBProject(
            name=project.project_name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            project_owner_id=user.employee_id,  
            project_status="In Progress"  
        )

        db.add(db_project)
        db.commit()

        for manager_id in project.manager_ids:
            manager = db.query(DBEmployee).filter(DBEmployee.employee_id == manager_id, DBEmployee.role == "manager").first()
            if not manager:
                raise HTTPException(status_code=404, detail=f"Manager with ID {manager_id} not found")
            db_employee_project = EmployeeProject(project_id=db_project.project_id, employee_id=manager_id)
            db.add(db_employee_project)

        for employee_id in project.employee_ids:
            employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id, DBEmployee.role == "member").first()
            if not employee:
                raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
            db_employee_project = EmployeeProject(project_id=db_project.project_id, employee_id=employee_id)
            db.add(db_employee_project)

        
        db.commit()
        db.refresh(db_project)

        return ProjectCreate(
            project_id=db_project.project_id,
            project_name=db_project.name,
            description=db_project.description,
            start_date=db_project.start_date,
            end_date=db_project.end_date,
            project_status=db_project.project_status,
            project_owner_id=db_project.project_owner_id,
            project_owner_name=user.name,  
            manager_ids=project.manager_ids,
            employee_ids=project.employee_ids
        )

    except HTTPException as e:
        raise e  
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

    
# Update Project by ID(ADMIN)
@app.put("/projects/{project_id}", response_model=ProjectUpdateResponse)
async def update_project(
    project_id: int,
    project: ProjectUpdate,  
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        
        db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()

        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == db_project.project_owner_id).first()

        if not project_owner:
            raise HTTPException(status_code=404, detail=f"Project owner with ID {db_project.project_owner_id} not found")

        db_project.name = project.project_name
        db_project.description = project.description
        db_project.start_date = project.start_date
        db_project.end_date = project.end_date
        # db_project.project_status= project.project_status
        # db_project.project_owner_id = project_owner.employee_id  

        db.query(EmployeeProject).filter(EmployeeProject.project_id == project_id).delete()

        for manager_id in project.manager_ids:
            manager = db.query(DBEmployee).filter(DBEmployee.employee_id == manager_id, DBEmployee.role == "manager").first()
            if not manager:
                raise HTTPException(status_code=404, detail=f"Manager with ID {manager_id} not found")
            db_employee_project = EmployeeProject(project_id=db_project.project_id, employee_id=manager_id)
            db.add(db_employee_project)

        for employee_id in project.employee_ids:
            employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id, DBEmployee.role == "member").first()
            if not employee:
                raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
            db_employee_project = EmployeeProject(project_id=db_project.project_id, employee_id=employee_id)
            db.add(db_employee_project)

        db.commit()
        db.refresh(db_project)

        return {
            "project_name": db_project.name,
            "description": db_project.description,
            "start_date": db_project.start_date,
            "end_date": db_project.end_date,

            "project_status": db_project.project_status,

            "project_owner_id": db_project.project_owner_id,
            "project_owner_name": project_owner.name,
            "managers": [manager_id for manager_id in project.manager_ids],
            "members": [employee_id for employee_id in project.employee_ids],
        }

    except HTTPException as e:
        raise e  
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e
    
#Update Project Status to Completed (ADMIN)
@app.post("/projects/mark-complete")
async def complete_project(
    project: ProjectComplete,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "manager":
        raise HTTPException(status_code=403, detail="Access forbidden: Managers only")
    
    try:
        db_project = db.query(DBProject).filter(DBProject.project_id == project.project_id).first()

        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        db_project.project_status = project.project_status

        db.commit()
        
        return {
            "project_id" : db_project.project_id,
            "project_status" : db_project.project_status
        }

    except HTTPException as e:
        raise e  
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e




#Delete Project by ID (ADMIN) 
@app.delete("/projects/{project_id}", response_model=dict)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()

        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")

        db.delete(db_project)
        db.commit()

        return {"message": f"Project with ID {project_id} has been deleted successfully"}

    except HTTPException as e:
        raise e  
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


# Get all managers (ADMIN)
@app.get("/managers", response_model=ManagerListResponse)
async def get_all_managers(
        db: Session = Depends(get_db), 
        user: DBEmployee = Depends(verify_jwt)
    ):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        managers = db.query(DBEmployee).filter(DBEmployee.role == "manager").all()

        if not managers:
            return ManagerListResponse(managers=[], manager_count=0)

        manager_list = [ManagerResponse.model_validate(manager) for manager in managers]

        return ManagerListResponse(
            managers=manager_list,
            manager_count=len(manager_list)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Get all members (ADMIN)
@app.get("/members", response_model=MemberListResponse)
async def get_all_members(
        db: Session = Depends(get_db), 
        user: DBEmployee = Depends(verify_jwt)
    ):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        members = db.query(DBEmployee).filter(DBEmployee.role == "member").all()

        if not members:
            return MemberListResponse(members=[], member_count=0)

        member_list = [MemberResponse.model_validate(member) for member in members]

        return MemberListResponse(
            members=member_list,
            member_count=len(member_list)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Get all employees (ADMIN, MANAGER)
@app.get("/employees", response_model=EmployeeListResponse)
async def get_all_employees(
        db: Session = Depends(get_db), 
        user: DBEmployee = Depends(verify_jwt)
    ):
    
    if user.role != "admin" and user.role != "manager":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins and Managers only")

    try:
        employees = db.query(DBEmployee).all()

        if not employees:
            return EmployeeListResponse(employees=[], employee_count=0)

        employee_list = [EmployeeResponse.model_validate(employee) for employee in employees]

        return EmployeeListResponse(
            employees=employee_list,
            employee_count=len(employee_list)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Change Roles (ADMIN)
@app.put("/change-role", response_model=EmployeeResponse)
async def update_employee_role(
    request: UpdateRoleRequest,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        employee = db.query(DBEmployee).filter(DBEmployee.employee_id == request.employee_id).first()

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        valid_roles = {"member", "manager", "admin"}
        if request.new_role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role: {request.new_role}. Allowed roles are {valid_roles}.")

        if employee.employee_id == user.employee_id:
            raise HTTPException(status_code=400, detail="You cannot change your own role.")

        employee.role = request.new_role

        if request.new_role == "member":
            db.query(EmployeeProject).filter(EmployeeProject.employee_id == request.employee_id).delete()
        elif request.new_role == "manager":
            db.query(EmployeeTask).filter(EmployeeTask.employee_id == request.employee_id).delete()
            db.query(EmployeeProject).filter(EmployeeProject.employee_id == request.employee_id).delete()

        db.commit()
        db.refresh(employee)

        return {
            "employee_id": employee.employee_id,
            "name": employee.name,
            "role": employee.role
        }

    except HTTPException as e:
        raise e  
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

@app.put("/tasks/update-status")
async def update_task_status(
    request: UpdateTaskStatusRequest,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt),
):
    
    if user.role not in {"member", "manager", "admin"}:
        raise HTTPException(status_code=403, detail="Access forbidden: Insufficient permissions.")

    try: 
        task = db.query(DBTask).filter(DBTask.task_id == request.task_id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")


        task.status = request.new_status

        try:
            db.commit()
            db.refresh(task)
            return {
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status,
                "due_date": task.due_date,
                "owner_id": task.task_owner_id,
            }
        except Exception as e:
            db.rollback()
            print(e)
            raise HTTPException(status_code=500, detail="An error occurred while updating task status") from e
    except HTTPException as e:
        print(e)
        raise e  
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


# Logout
# @app.post("/logout", response_model=dict)
# async def logout(response: RedirectResponse):
    
#     response.set_cookie(
#         key="access_token", 
#         value="", 
#         max_age=0,  # Expire the cookie
#         httponly=True,  # Make sure it's HTTP-only to prevent JS access
#         expires=0  # Set expires to 0, which removes the cookie
#     )

#     return RedirectResponse(url="http://localhost:5173/login")

# Create a new task and assign employees (ADMIN, MANAGER)
@app.post("/tasks/{project_id}",response_model=Task)
async def create_task(
    task: TaskCreate,
    project_id: int,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "admin" and user.role != "manager":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        db_task = DBTask(
            name=task.name,
            description=task.description,
            due_date=task.due_date,
            project_id=project_id,
            status="Not Started",  
            task_owner_id=user.employee_id  
        )

        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        for employee_id in task.employee_ids:
            employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id, DBEmployee.role == "member").first()
            if not employee:
                raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
            db_employee_task = EmployeeTask(task_id=db_task.task_id, employee_id=employee_id)
            db.add(db_employee_task)

        db.commit()

        return Task(
            task_id=db_task.task_id,
            name=db_task.name,
            description=db_task.description,
            due_date=db_task.due_date,
            project_id=db_task.project_id,
            task_status=db_task.status,
            task_owner_id=db_task.task_owner_id,
            task_owner_name=user.name,  
            employee_ids=task.employee_ids
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


# Get all tasks for a specific project (ADMIN, MANAGER)
@app.get("/projects/tasks/{project_id}", response_model=TaskListResponse)
async def get_tasks_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role not in {"admin", "manager"}:
        raise HTTPException(status_code=403, detail="Access forbidden: Admins and Managers only")

    try:
        db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        db_tasks = db.query(DBTask).filter(DBTask.project_id == project_id).all()

        task_list = []
        for task in db_tasks:
            task_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == task.task_owner_id).first()
            if not task_owner:
                raise HTTPException(status_code=404, detail=f"Task owner with ID {task.task_owner_id} not found")

            employees = db.query(DBEmployee).join(EmployeeTask).filter(EmployeeTask.task_id == task.task_id).all()

            task_list.append(TaskResponse(
                task_id=task.task_id,
                name=task.name,
                description=task.description,
                due_date=task.due_date,
                status=task.status,
                task_owner_id=task.task_owner_id,
                task_owner_name=task_owner.name,
                #employee_names=[employee.name for employee in employees]
                members=[{"employee_id" : member.employee_id, "name" : member.name} for member in employees]
            ))

        return TaskListResponse(
            tasks=task_list,
            task_count=len(task_list)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error while fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Update a task (ADMIN, MANAGER)
@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role not in {"admin", "manager"}:
        raise HTTPException(status_code=403, detail="Access forbidden: Admins and Managers only")

    try:
        db_task = db.query(DBTask).filter(DBTask.task_id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        if task_update.name:
            db_task.name = task_update.name
        if task_update.description:
            db_task.description = task_update.description
        if task_update.due_date:
            db_task.due_date = task_update.due_date


        if task_update.employee_ids is not None:
            db.query(EmployeeTask).filter(EmployeeTask.task_id == task_id).delete()
            db.commit()

            for employee_id in task_update.employee_ids:
                employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id, DBEmployee.role == "member").first()
                if not employee:
                    raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
                db_employee_task = EmployeeTask(task_id=task_id, employee_id=employee_id)
                db.add(db_employee_task)

        db.commit()
        db.refresh(db_task)

        employees = db.query(DBEmployee).join(EmployeeTask).filter(EmployeeTask.task_id == task_id).all()
        return Task(
            task_id=db_task.task_id,
            name=db_task.name,
            description=db_task.description,
            due_date=db_task.due_date,
            project_id=db_task.project_id,
            task_status=db_task.status,
            task_owner_id=db_task.task_owner_id,
            task_owner_name=user.name,  
            employee_ids=[employee.employee_id for employee in employees]
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error while updating task: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Delete a task (ADMIN, MANAGER)
@app.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role not in {"admin", "manager"}:
        raise HTTPException(status_code=403, detail="Access forbidden: Admins and Managers only")

    try:
        db_task = db.query(DBTask).filter(DBTask.task_id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        db.query(EmployeeTask).filter(EmployeeTask.task_id == task_id).delete()

        db.delete(db_task)
        db.commit()

        return {"message": f"Task with ID {task_id} successfully deleted"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error while deleting task: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


# Get all projects for a specific employee
@app.get("/employees/{employee_id}/projects", response_model=EmployeeProjectsListResponse)
async def get_projects_for_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "admin" and user.role != "manager" and user.employee_id != employee_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        db_employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")

        assigned_projects = db.query(DBProject).join(EmployeeProject).filter(
            EmployeeProject.employee_id == employee_id
        ).all()

        project_list = []
        for project in assigned_projects:
            project_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == project.project_owner_id).first()
            if not project_owner:
                raise HTTPException(status_code=404, detail=f"Owner for project {project.project_id} not found")

            project_list.append(EmployeeProjectResponse(
                project_id=project.project_id,
                project_name=project.name,
                description=project.description,
                start_date=project.start_date,
                end_date=project.end_date,
                project_status=project.project_status,
                project_owner_id=project.project_owner_id,
                project_owner_name=project_owner.name
            ))

        return EmployeeProjectsListResponse(
            projects=project_list,
            project_count=len(project_list)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error while fetching projects for employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


# Get all tasks for a specific employee and project
@app.get("/projects/{project_id}/employees/{employee_id}/tasks", response_model=EmployeeTasksListResponse)
async def get_tasks_for_employee(
    employee_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "admin" and user.role != "manager" and user.employee_id != employee_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        db_employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")

        assigned_tasks = db.query(DBTask).join(EmployeeTask).filter(
            EmployeeTask.employee_id == employee_id, DBTask.project_id == project_id
        ).all()

        task_list = []
        for task in assigned_tasks:
            project = db.query(DBProject).filter(DBProject.project_id == task.project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail=f"Project for task {task.task_id} not found")

            task_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == task.task_owner_id).first()
            if not task_owner:
                raise HTTPException(status_code=404, detail=f"Owner for task {task.task_id} not found")

            task_list.append(EmployeeTaskResponse(
                task_id=task.task_id,
                name=task.name,
                description=task.description,
                due_date=task.due_date,
                status=task.status,
                project_id=task.project_id,
                project_name=project.name,
                task_owner_id=task.task_owner_id,
                task_owner_name=task_owner.name
            ))

        return EmployeeTasksListResponse(
            tasks=task_list,
            task_count=len(task_list)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error while fetching tasks for employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e
    
# Get a task from task_id
@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)  
):

    try:

        task = db.query(DBTask).filter(DBTask.task_id == task_id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        project = db.query(DBProject).filter(DBProject.project_id == task.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found for this task")

        task_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == task.task_owner_id).first()
        if not task_owner:
            raise HTTPException(status_code=404, detail="Task owner not found")

        members = db.query(DBEmployee).join(EmployeeTask).filter(EmployeeTask.task_id == task.task_id, DBEmployee.role == "member").all()
   
        return TaskResponse(
            task_id=task.task_id,
            name = task.name,
            description=task.description,
            due_date=task.due_date,
            status=task.status,
            task_owner_id=task.task_owner_id,
            task_owner_name=task_owner.name,
            project_id=task.project_id,
            project_name=project.name,
            #employee_names=[employee.name for employee in employees]
            members=[{"employee_id" : member.employee_id, "name" : member.name} for member in members],
        )

    except HTTPException as e:
        raise e  
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e








