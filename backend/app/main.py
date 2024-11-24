import os
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
from models import Project as DBProject, Task as DBTask, Employee as DBEmployee, EmployeeTask, EmployeeProject 
from schemas import ProjectCreate, ProjectResponse, Task, TaskCreate, Employee, EmployeeCreate, ManagerResponse, EmployeeResponse, RoleUpdateRequest
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
            raise HTTPException(status_code=400, detail="Invalid token")
        
        employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return employee
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    

# Get all projects (ADMIN)
@app.get("/projects/", response_model=List[ProjectResponse])
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
            # Fetch the project owner
            project_owner = db.query(DBEmployee).filter(DBEmployee.employee_id == project.project_owner_id).first()
            if not project_owner:
                raise HTTPException(status_code=404, detail=f"Project owner with ID {project.project_owner_id} not found")

            # Fetch managers
            managers = db.query(DBEmployee).join(EmployeeProject).filter(
                EmployeeProject.project_id == project.project_id, DBEmployee.role == "manager"
            ).all()

            # Fetch employees
            employees = db.query(DBEmployee).join(EmployeeProject).filter(
                EmployeeProject.project_id == project.project_id, DBEmployee.role == "member"
            ).all()

            # Add project details to the response list
            project_list.append({
                "project_name": project.name,
                "description": project.description,
                "start_date": project.start_date,
                "end_date": project.end_date,
                "project_owner_id": project.project_owner_id,
                "project_owner_name": project_owner.name,
                "managers": [manager.employee_id for manager in managers],
                "employees": [employee.employee_id for employee in employees],
            })

        return project_list

    except HTTPException as e:
        # Explicitly raised HTTPExceptions are returned as-is
        raise e
    except Exception as e:
        # Catch other unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


# Create a new project with assigned managers and employees (ADMIN)
@app.post("/projects/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Step 1: Create the project
        db_project = DBProject(
            name=project.project_name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            project_owner_id=project.project_owner_id,
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)

        # Step 2: Assign managers to the project
        for manager_id in project.managers:
            manager = db.query(DBEmployee).filter(DBEmployee.employee_id == manager_id, DBEmployee.role == "manager").first()
            if not manager:
                raise HTTPException(status_code=404, detail=f"Manager with ID {manager_id} not found")
            db_employee_project = EmployeeProject(project_id=db_project.project_id, employee_id=manager_id)
            db.add(db_employee_project)

        # Step 3: Assign employees to the project
        for employee_id in project.employees:
            employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id, DBEmployee.role == "member").first()
            if not employee:
                raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
            db_employee_project = EmployeeProject(project_id=db_project.project_id, employee_id=employee_id)
            db.add(db_employee_project)

        db.commit()

        # Step 4: Return a minimal response (or success message)
        return {
            "project_id": db_project.project_id,
            "message": "Project created successfully"
        }

    except HTTPException as e:
        raise e  
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e
    
# Update Project by ID(ADMIN)
@app.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectCreate,  # Pydantic model for project creation
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

        # Update the project fields
        db_project.name = project.project_name
        db_project.description = project.description
        db_project.start_date = project.start_date
        db_project.end_date = project.end_date
        db_project.project_owner_id = project.project_owner_id  # Ensure the owner is valid

        # Commit the changes to the database
        db.commit()
        db.refresh(db_project)

        # Return the updated project details
        return {
            "project_name": db_project.name,
            "description": db_project.description,
            "start_date": db_project.start_date,
            "end_date": db_project.end_date,
            "project_owner_id": db_project.project_owner_id,
            "project_owner_name": user.name,  # Assuming the creator's name is the project owner
            "managers": [manager.employee_id for manager in db_project.managers],
            "employees": [employee.employee_id for employee in db_project.employees],
        }

    except HTTPException as e:
        raise e  # Return explicitly raised HTTP exceptions
    except Exception as e:
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
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Get all managers (ADMIN)
@app.get("/managers/", response_model=List[ManagerResponse])
async def get_all_managers(db: Session = Depends(get_db), user: DBEmployee = Depends(verify_jwt)):
    # Only admins can view all managers
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Fetch all managers from the database
        managers = db.query(DBEmployee).filter(DBEmployee.role == "manager").all()

        # If no managers are found
        if not managers:
            raise HTTPException(status_code=404, detail="No managers found")

        return managers

    except HTTPException as e:
        raise e  # Explicitly raised HTTPExceptions are returned as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Get all employees (ADMIN)
@app.get("/employees/", response_model=List[EmployeeResponse])
async def get_all_employees(db: Session = Depends(get_db), user: DBEmployee = Depends(verify_jwt)):
    # Only admins can view all employees
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Fetch all employees from the database
        employees = db.query(DBEmployee).all()

        # If no employees are found
        if not employees:
            raise HTTPException(status_code=404, detail="No employees found")

        return employees

    except HTTPException as e:
        raise e  # Explicitly raised HTTPExceptions are returned as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Change Roles (ADMIN)
@app.put("/employees/{employee_id}/role", response_model=EmployeeResponse)
async def update_employee_role(
    employee_id: int,
    role_update: RoleUpdateRequest,
    db: Session = Depends(get_db),
    user: DBEmployee = Depends(verify_jwt)
):
    # Only admins can update employee roles
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    try:
        # Fetch the employee from the database
        employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Validate the new role
        if role_update.new_role not in ["manager", "employee"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'manager' or 'employee'.")

        # Update the employee's role
        employee.role = role_update.new_role

        # Commit the change to the database
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











# Create a new task for a list of employees
@app.post("/tasks/", response_model=Task)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Step 1: Create the task
    db_task = DBTask(
        description=task.description,
        due_date=task.due_date,
        status="new",  # Automatically set the status to "new"
        task_owner=task.task_owner,  # The task creator
        project_id=task.project_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Step 2: Assign employees to the task
    for employee_id in task.employee_ids:
        # Check if the employee exists
        db_employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")

        # Create the association in EmployeeTask table
        db_employee_task = EmployeeTask(employee_id=employee_id, task_id=db_task.task_id)
        db.add(db_employee_task)

    db.commit()

    # Return the created task with its details
    return db_task


# Get all tasks
@app.get("/tasks/", response_model=List[Task])
async def get_tasks(request: Request, db: Session = Depends(get_db)):
    print(request.cookies)
    tasks = db.query(DBTask).all()
    return tasks


# Get all tasks for a specific project
@app.get("/tasks/{project_id}", response_model=List[Task])
async def get_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
    tasks = db.query(DBTask).filter(DBTask.project_id == project_id).all()
    return tasks

# Get all tasks for a specific project and employee
@app.get("/tasks/{project_id}/employee/{employee_id}", response_model=List[Task])
async def get_tasks_by_project_and_employee(project_id: int, employee_id: int, db: Session = Depends(get_db)):
    # Query tasks that match the project_id and employee_id
    tasks = db.query(DBTask).join(EmployeeTask).filter(DBTask.project_id == project_id, EmployeeTask.employee_id == employee_id).all()

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for this project and employee")

    return tasks

#Get all tasks for a specific project and task owner
@app.get("/tasks/{project_id}/owner/{task_owner}", response_model=List[Task])
async def get_tasks_by_project_and_owner(project_id: int, task_owner: str, db: Session = Depends(get_db)):
    # Query tasks for a specific project and owner
    tasks = db.query(DBTask).filter(DBTask.project_id == project_id, DBTask.owner == task_owner).all()

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for the given project and owner")

    return tasks


# Update a task by ID
@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(DBTask).filter(DBTask.task_id == task_id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update the fields of the task
    db_task.description = task.description
    db_task.due_date = task.due_date
    db_task.status = task.status
    db_task.task_owner = task.task_owner
    db_task.project_id = task.project_id

    db.commit()
    db.refresh(db_task)

    return db_task


# Delete a task by ID
@app.delete("/tasks/{task_id}", response_model=Task)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(DBTask).filter(DBTask.task_id == task_id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()

    return db_task


# Create an Employee
@app.post("/employees/", response_model=Employee)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = DBEmployee(
        name=employee.name, 
        email_id=employee.email_id, 
        role=employee.role
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# Get All Employees
@app.get("/employees/", response_model=List[Employee])
async def get_all_employees(db: Session = Depends(get_db)):
    employees = db.query(DBEmployee).all()
    return employees

# Get an Employee by ID
@app.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

# Update an Employee
@app.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Update fields
    db_employee.name = employee.name
    db_employee.email_id = employee.email_id
    db_employee.role = employee.role

    db.commit()
    db.refresh(db_employee)
    return db_employee

# Delete an Employee
@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db.delete(db_employee)
    db.commit()
    return {"message": f"Employee with ID {employee_id} deleted successfully"}


