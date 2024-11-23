# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Project as DBProject, Task as DBTask, Employee as DBEmployee, EmployeeTask, EmployeeProject  # SQLAlchemy model
from schemas import Project, ProjectCreate, Task, TaskCreate, Employee, EmployeeCreate # Pydantic models
from database import SessionLocal, engine, Base

# Create tables in the database (run this once to initialize)
# Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#############################################################################

# # Create a new project
# @app.post("/projects/", response_model=Project)  # Use Pydantic Project model for response
# async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
#     db_project = DBProject(
#         name=project.name,
#         description=project.description,
#         start_date=project.start_date,
#         end_date=project.end_date,
#         project_owner=project.project_owner,
#     )
#     db.add(db_project)
#     db.commit()
#     db.refresh(db_project)
#     return db_project  # FastAPI will use the Project Pydantic model for serialization

# Create a new project with assigned employees
@app.post("/projects/", response_model=Project)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # Step 1: Create the project
    db_project = DBProject(
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        project_owner=project.project_owner
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Step 2: Assign employees to the project
    for employee_id in project.employee_ids:
        # Check if the employee exists
        db_employee = db.query(DBEmployee).filter(DBEmployee.employee_id == employee_id).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
        
        # Create the association in EmployeeProject table
        db_employee_project = EmployeeProject(project_id=db_project.project_id, employee_id=employee_id)
        db.add(db_employee_project)

    db.commit()

    # Return the project details along with the assigned employees
    return db_project

# Get all projects
@app.get("/projects/", response_model=List[Project])  # Use Pydantic Project model for response
async def get_projects(db: Session = Depends(get_db)):
    projects = db.query(DBProject).all()
    return projects  # FastAPI will use the Project Pydantic model for serialization

# Get all projects for a specific employee
@app.get("/projects/employee/{employee_id}", response_model=List[Project])
async def get_projects_for_employee(employee_id: int, db: Session = Depends(get_db)):
    # Query projects associated with tasks assigned to the given employee
    projects = db.query(DBProject).join(DBTask).join(EmployeeTask).filter(EmployeeTask.employee_id == employee_id).all()

    if not projects:
        raise HTTPException(status_code=404, detail="No projects found for this employee")

    return projects


# Delete project by ID
@app.delete("/projects/{project_id}", response_model=Project)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    # Fetch the project by ID
    db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()
    
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete the project
    db.delete(db_project)
    db.commit()

    return db_project  # Return the deleted project (optional, for confirmation)


# Update project by ID
@app.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    # Fetch the project by ID
    db_project = db.query(DBProject).filter(DBProject.project_id == project_id).first()
    
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update the fields of the project
    db_project.name = project.name
    db_project.description = project.description
    db_project.start_date = project.start_date
    db_project.end_date = project.end_date
    db_project.project_owner = project.project_owner

    # Commit the changes to the database
    db.commit()
    db.refresh(db_project)

    return db_project  # Return the updated project


#####################################################################################



# # Create a new task
# @app.post("/tasks/", response_model=Task)
# async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
#     db_task = DBTask(
#         description=task.description,
#         due_date=task.due_date,
#         status="not started",
#         task_owner=task.owner,
#         project_id=task.project_id
#     )
#     db.add(db_task)
#     db.commit()
#     db.refresh(db_task)
#     return db_task

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
async def get_tasks(db: Session = Depends(get_db)):
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


########################################################################################

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


