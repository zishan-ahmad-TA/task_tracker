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
@app.get("/projects/", response_model=ProjectListResponse)
async def get_projects(
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Fetch all projects from the database
        projects = db.query(DBProject).all()

        # Prepare the project response list
        project_list = []
        for project in projects:
            # Fetch the project owner
            project_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == project.project_owner_id).first()
            if not project_owner:
                raise HTTPException(status_code=404, detail=f"Project owner with ID {project.project_owner_id} not found")

            # Fetch managers
            managers = db.query(DBEmployee).join(EmployeeProject).filter(
                EmployeeProject.project_id == project.project_id, DBEmployee.role == "manager"
            ).all()

            # Fetch employees
            members = db.query(DBEmployee).join(EmployeeProject).filter(
                EmployeeProject.project_id == project.project_id, DBEmployee.role == "member"
            ).all()

            # Append project details in the format required by ProjectResponse
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

        # Return the response in the format required by ProjectListResponse
        return ProjectListResponse(
            projects=project_list,
            project_count=len(projects)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Get project by id (ADMIN / MANAGER only)
@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(
    project_id: int, 
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)  # If you want to validate user role or permissions
):

    if user.role != "admin" and user.role != "manager":
        raise HTTPException(status_code=403, detail="Access forbidden: Unauthorized User")

    try:
        # Fetch the project from the database
        project = db.query(DBProject).filter(DBProject.project_id == project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Fetch the project owner
        project_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == project.project_owner_id).first()
        if not project_owner:
            raise HTTPException(status_code=404, detail="Project owner not found")

        # Fetch managers assigned to the project
        managers = db.query(DBEmployee).join(EmployeeProject).filter(
            EmployeeProject.project_id == project.project_id, DBEmployee.role == "manager"
        ).all()

        # Fetch employees assigned to the project
        members = db.query(DBEmployee).join(EmployeeProject).filter(
            EmployeeProject.project_id == project.project_id, DBEmployee.role == "member"
        ).all()

        # Return the project details
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
        raise e  # Explicitly raised HTTPExceptions are returned as-is
    except Exception as e:
        # Catch other unexpected errors
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e



# Create a new project with assigned managers and employees (ADMIN)
@app.post("/projects/", response_model=ProjectCreate)
async def create_project(
    project: ProjectBase,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    # Ensure the user is an admin
    if user.role != "admin":
       raise HTTPException(status_code=403, detail="Access forbidden: Admins only")


    try:
        # Step 1: Create the project with default status and project owner from the logged-in user
        db_project = DBProject(
            name=project.project_name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            project_owner_id=user.employee_id,  # Extract owner from logged-in user
            project_status="In Progress"  # Default project status
        )

        db.add(db_project)
        db.commit()

        # Step 2: Assign managers to the project
        for manager_id in project.manager_ids:
            manager = db.query(DBEmployee).filter(DBEmployee.employee_id == manager_id, DBEmployee.role == "manager").first()
            if not manager:
                raise HTTPException(status_code=404, detail=f"Manager with ID {manager_id} not found")
            db_employee_project = EmployeeProject(project_id=db_project.project_id, employee_id=manager_id)
            db.add(db_employee_project)

        # Step 3: Assign employees to the project
        for employee_id in project.employee_ids:
            employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id, DBEmployee.role == "member").first()
            if not employee:
                raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
            db_employee_project = EmployeeProject(project_id=db_project.project_id, employee_id=employee_id)
            db.add(db_employee_project)

        
        db.commit()
        db.refresh(db_project)

        # Step 4: Return the project details
        return ProjectCreate(
            project_id=db_project.project_id,
            project_name=db_project.name,
            description=db_project.description,
            start_date=db_project.start_date,
            end_date=db_project.end_date,
            project_status=db_project.project_status,
            project_owner_id=db_project.project_owner_id,
            project_owner_name=user.name,  # Owner name from logged-in user
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
    project: ProjectUpdate,  # Pydantic model for project creation
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    # Only admins can update projects
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        
        # Fetch the existing project by project_id
        db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()

        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == db_project.project_owner_id).first()

        if not project_owner:
            raise HTTPException(status_code=404, detail=f"Project owner with ID {db_project.project_owner_id} not found")

        # Update the project fields
        db_project.name = project.project_name
        db_project.description = project.description
        db_project.start_date = project.start_date
        db_project.end_date = project.end_date
        # db_project.project_status= project.project_status
        # db_project.project_owner_id = project_owner.employee_id  # Ensure the owner is valid

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

        # Return the updated project details
        return {
            "project_name": db_project.name,
            "description": db_project.description,
            "start_date": db_project.start_date,
            "end_date": db_project.end_date,

            #Require addition of project status (in the table as well)
            "project_status": db_project.project_status,

            "project_owner_id": db_project.project_owner_id,
            "project_owner_name": project_owner.name,
            "managers": [manager_id for manager_id in project.manager_ids],
            "members": [employee_id for employee_id in project.employee_ids],
        }

    except HTTPException as e:
        raise e  # Return explicitly raised HTTP exceptions
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
    # Only admins can delete projects
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Fetch the project by project_id
        db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()

        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete the project from the database
        db.delete(db_project)
        db.commit()

        # Return success message
        return {"message": f"Project with ID {project_id} has been deleted successfully"}

    except HTTPException as e:
        raise e  # Return explicitly raised HTTP exceptions
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


# Get all managers (ADMIN)
@app.get("/managers/", response_model=ManagerListResponse)
async def get_all_managers(
        db: Session = Depends(get_db), 
        user: DBEmployee = Depends(verify_jwt)
    ):
    # Only admins can view all managers
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Fetch all managers from the database
        managers = db.query(DBEmployee).filter(DBEmployee.role == "manager").all()

        # If no managers are found, return an empty ManagerListResponse
        if not managers:
            return ManagerListResponse(managers=[], manager_count=0)

        # Convert SQLAlchemy objects to Pydantic models
        manager_list = [ManagerResponse.model_validate(manager) for manager in managers]

        # Return the ManagerListResponse
        return ManagerListResponse(
            managers=manager_list,
            manager_count=len(manager_list)
        )

    except HTTPException as e:
        # Explicitly raised HTTPExceptions are returned as-is
        raise e
    except Exception as e:
        # Catch other unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Get all members (ADMIN)
@app.get("/members/", response_model=MemberListResponse)
async def get_all_members(
        db: Session = Depends(get_db), 
        user: DBEmployee = Depends(verify_jwt)
    ):
    # Only admins can view all managers
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Fetch all managers from the database
        members = db.query(DBEmployee).filter(DBEmployee.role == "member").all()

        # If no managers are found, return an empty ManagerListResponse
        if not members:
            return MemberListResponse(members=[], member_count=0)

        # Convert SQLAlchemy objects to Pydantic models
        member_list = [MemberResponse.model_validate(member) for member in members]

        # Return the ManagerListResponse
        return MemberListResponse(
            members=member_list,
            member_count=len(member_list)
        )

    except HTTPException as e:
        # Explicitly raised HTTPExceptions are returned as-is
        raise e
    except Exception as e:
        # Catch other unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Get all employees (ADMIN, MANAGER)
@app.get("/employees/", response_model=EmployeeListResponse)
async def get_all_employees(
        db: Session = Depends(get_db), 
        user: DBEmployee = Depends(verify_jwt)
    ):
    
    if user.role != "admin" and user.role != "manager":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins and Managers only")

    try:
        # Fetch all employees from the database
        employees = db.query(DBEmployee).all()

        # If no employees are found, return an empty EmployeeListResponse
        if not employees:
            return EmployeeListResponse(employees=[], employee_count=0)

        # Convert SQLAlchemy objects to Pydantic models
        employee_list = [EmployeeResponse.model_validate(employee) for employee in employees]

        # Return the EmployeeListResponse
        return EmployeeListResponse(
            employees=employee_list,
            employee_count=len(employee_list)
        )

    except HTTPException as e:
        # Explicitly raised HTTPExceptions are returned as-is
        raise e
    except Exception as e:
        # Catch other unexpected errors
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Change Roles (ADMIN)
@app.put("/change-role/", response_model=EmployeeResponse)
async def update_employee_role(
    request: UpdateRoleRequest,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    # Only admins can update employee roles
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Fetch the employee from the database
        employee = db.query(DBEmployee).filter(DBEmployee.employee_id == request.employee_id).first()

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Validate the new role
        valid_roles = {"member", "manager", "admin"}
        if request.new_role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role: {request.new_role}. Allowed roles are {valid_roles}.")

        # Prevent self-demotion
        if employee.employee_id == user.employee_id:
            raise HTTPException(status_code=400, detail="You cannot change your own role.")

        # Assign the new role
        employee.role = request.new_role

        # Wipe corresponding table details (if applicable)
        if request.new_role == "member":
            db.query(EmployeeProject).filter(EmployeeProject.employee_id == request.employee_id).delete()
        elif request.new_role == "manager":
            db.query(EmployeeTask).filter(EmployeeTask.employee_id == request.employee_id).delete()
            db.query(EmployeeProject).filter(EmployeeProject.employee_id == request.employee_id).delete()

        # Commit changes to the database
        db.commit()
        db.refresh(employee)

        # Return the updated employee details
        return {
            "employee_id": employee.employee_id,
            "name": employee.name,
            "role": employee.role
        }

    except HTTPException as e:
        raise e  # Return explicitly raised HTTPExceptions as-is
    except Exception as e:
        # Log the exception for debugging (not shown here)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e



# Logout
@app.post("/logout", response_model=dict)
async def logout(response: RedirectResponse):
    
    response.set_cookie(
        key="access_token", 
        value="", 
        max_age=0,  # Expire the cookie
        httponly=True,  # Make sure it's HTTP-only to prevent JS access
        expires=0  # Set expires to 0, which removes the cookie
    )

    return RedirectResponse(url="http://localhost:5173/login")

# Create a new task and assign employees (ADMIN, MANAGER)
@app.post("/tasks/{project_id}",response_model=Task)
async def create_task(
    task: TaskCreate,
    project_id: int,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    # Ensure the user is an admin or manager
    if user.role != "admin" and user.role != "manager":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Step 1: Validate that the project exists
        db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        # Step 2: Create the task
        db_task = DBTask(
            name=task.name,
            description=task.description,
            due_date=task.due_date,
            project_id=project_id,
            status="Not Started",  # Default task status
            task_owner_id=user.employee_id  # Logged-in user is the task owner
        )

        

        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        # Step 3: Assign employees to the task
        for employee_id in task.employee_ids:
            employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id, DBEmployee.role == "member").first()
            if not employee:
                raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
            db_employee_task = EmployeeTask(task_id=db_task.task_id, employee_id=employee_id)
            db.add(db_employee_task)

        db.commit()

        # Step 4: Return the task details
        return Task(
            task_id=db_task.task_id,
            name=db_task.name,
            description=db_task.description,
            due_date=db_task.due_date,
            project_id=db_task.project_id,
            task_status=db_task.status,
            task_owner_id=db_task.task_owner_id,
            task_owner_name=user.name,  # Owner name from logged-in user
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
    # Step 1: Role-based access control
    if user.role not in {"admin", "manager"}:
        raise HTTPException(status_code=403, detail="Access forbidden: Admins and Managers only")

    try:
        # Step 2: Validate that the project exists
        db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        # Step 3: Fetch all tasks for the project
        db_tasks = db.query(DBTask).filter(DBTask.project_id == project_id).all()

        # Step 4: Prepare the task response list
        task_list = []
        for task in db_tasks:
            # Fetch the task owner
            task_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == task.task_owner_id).first()
            if not task_owner:
                raise HTTPException(status_code=404, detail=f"Task owner with ID {task.task_owner_id} not found")

            # Fetch the employees assigned to the task
            employees = db.query(DBEmployee).join(EmployeeTask).filter(EmployeeTask.task_id == task.task_id).all()

            # Append task details to the response list
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

        # Step 5: Return the response in the required format
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
    # Step 1: Role-based access control
    if user.role not in {"admin", "manager"}:
        raise HTTPException(status_code=403, detail="Access forbidden: Admins and Managers only")

    try:
        # Step 2: Fetch the task
        db_task = db.query(DBTask).filter(DBTask.task_id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        # Step 3: Update task details if provided
        if task_update.name:
            db_task.name = task_update.name
        if task_update.description:
            db_task.description = task_update.description
        if task_update.due_date:
            db_task.due_date = task_update.due_date


        # Step 4: Update assigned employees if provided
        if task_update.employee_ids is not None:
            # Clear current employee assignments
            db.query(EmployeeTask).filter(EmployeeTask.task_id == task_id).delete()
            db.commit()

            # Re-assign employees
            for employee_id in task_update.employee_ids:
                employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id, DBEmployee.role == "member").first()
                if not employee:
                    raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
                db_employee_task = EmployeeTask(task_id=task_id, employee_id=employee_id)
                db.add(db_employee_task)

        # Save changes
        db.commit()
        db.refresh(db_task)

        # Step 5: Return the updated task details
        employees = db.query(DBEmployee).join(EmployeeTask).filter(EmployeeTask.task_id == task_id).all()
        return Task(
            task_id=db_task.task_id,
            name=db_task.name,
            description=db_task.description,
            due_date=db_task.due_date,
            project_id=db_task.project_id,
            task_status=db_task.status,
            task_owner_id=db_task.task_owner_id,
            task_owner_name=user.name,  # Owner name from logged-in user
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
    # Step 1: Role-based access control
    if user.role not in {"admin", "manager"}:
        raise HTTPException(status_code=403, detail="Access forbidden: Admins and Managers only")

    try:
        # Step 2: Fetch the task
        db_task = db.query(DBTask).filter(DBTask.task_id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        # Step 3: Delete associated employee assignments
        db.query(EmployeeTask).filter(EmployeeTask.task_id == task_id).delete()

        # Step 4: Delete the task
        db.delete(db_task)
        db.commit()

        # Step 5: Return confirmation
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
    # Allow only admins, managers, or the employee themself to access the data
    if user.role != "admin" and user.role != "manager" and user.employee_id != employee_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        # Step 1: Validate that the employee exists
        db_employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")

        # Step 2: Fetch all projects assigned to the employee
        assigned_projects = db.query(DBProject).join(EmployeeProject).filter(
            EmployeeProject.employee_id == employee_id
        ).all()

        # Step 3: Prepare the response
        project_list = []
        for project in assigned_projects:
            # Fetch the project owner
            project_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == project.project_owner_id).first()
            if not project_owner:
                raise HTTPException(status_code=404, detail=f"Owner for project {project.project_id} not found")

            # Add project details to the response list
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

        # Return the list of projects
        return EmployeeProjectsListResponse(
            projects=project_list,
            project_count=len(project_list)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error while fetching projects for employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


# Get all tasks for a specific employee
@app.get("/employees/{employee_id}/tasks", response_model=EmployeeTasksListResponse)
async def get_tasks_for_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    # Allow only admins, managers, or the employee themselves to access the data
    if user.role != "admin" and user.role != "manager" and user.employee_id != employee_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        # Step 1: Validate that the employee exists
        db_employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")

        # Step 2: Fetch all tasks assigned to the employee
        assigned_tasks = db.query(DBTask).join(EmployeeTask).filter(
            EmployeeTask.employee_id == employee_id
        ).all()

        # Step 3: Prepare the response
        task_list = []
        for task in assigned_tasks:
            # Fetch the project associated with the task
            project = db.query(DBProject).filter(DBProject.project_id == task.project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail=f"Project for task {task.task_id} not found")

            # Fetch the task owner
            task_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == task.task_owner_id).first()
            if not task_owner:
                raise HTTPException(status_code=404, detail=f"Owner for task {task.task_id} not found")

            # Add task details to the response list
            task_list.append(EmployeeTaskResponse(
                task_id=task.task_id,
                task_name=task.name,
                description=task.description,
                due_date=task.due_date,
                task_status=task.status,
                project_id=task.project_id,
                project_name=project.name,
                task_owner_id=task.task_owner_id,
                task_owner_name=task_owner.name
            ))

        # Return the list of tasks
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
    user: DBEmployee = Depends(verify_jwt)  # Optional: If you want to validate user role or permissions
):

    try:
        print("hello")
        # Fetch the task from the database
        task = db.query(DBTask).filter(DBTask.task_id == task_id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Fetch the associated project for the task
        project = db.query(DBProject).filter(DBProject.project_id == task.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found for this task")

        # Fetch the task owner (employee assigned to the task)
        task_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == task.task_owner_id).first()
        if not task_owner:
            raise HTTPException(status_code=404, detail="Task owner not found")

        # Fetch employees assigned to the task (if any)
        members = db.query(DBEmployee).join(EmployeeTask).filter(EmployeeTask.task_id == task.task_id, DBEmployee.role == "member").all()
   

        # Return the task details along with related information
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
        raise e  # Return explicitly raised HTTPExceptions as-is
    except Exception as e:
        # Catch any unexpected errors
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e








