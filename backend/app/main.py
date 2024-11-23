# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Project as DBProject, Task as DBTask, EmployeeTask  # SQLAlchemy model
from schemas import Project, ProjectCreate, Task, TaskCreate # Pydantic models
from database import SessionLocal, engine

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

# Create a new project
@app.post("/projects/", response_model=Project)  # Use Pydantic Project model for response
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = DBProject(
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        owner=project.owner,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project  # FastAPI will use the Project Pydantic model for serialization

# Get all projects
@app.get("/projects/", response_model=List[Project])  # Use Pydantic Project model for response
async def get_projects(db: Session = Depends(get_db)):
    projects = db.query(DBProject).all()
    return projects  # FastAPI will use the Project Pydantic model for serialization

# Get all projects for a specific employee
@app.get("/projects/employee/{employee_id}", response_model=List[Project])
async def get_projects_for_employee(employee_id: int, db: Session = Depends(get_db)):
    # Query projects associated with tasks assigned to the given employee
    projects = db.query(Project).join(Task).join(EmployeeTask).filter(EmployeeTask.employee_id == employee_id).all()

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
    db_project.owner = project.owner

    # Commit the changes to the database
    db.commit()
    db.refresh(db_project)

    return db_project  # Return the updated project


#####################################################################################



# Create a new task
@app.post("/tasks/", response_model=Task)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = DBTask(
        description=task.description,
        due_date=task.due_date,
        status=task.status,
        owner=task.owner,
        project_id=task.project_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# Get all tasks
@app.get("/tasks/", response_model=List[Task])
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks


# Get all tasks for a specific project
@app.get("/tasks/{project_id}", response_model=List[Task])
async def get_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return tasks

# Get all tasks for a specific project and employee
@app.get("/tasks/{project_id}/employee/{employee_id}", response_model=List[Task])
async def get_tasks_by_project_and_employee(project_id: int, employee_id: int, db: Session = Depends(get_db)):
    # Query tasks that match the project_id and employee_id
    tasks = db.query(Task).join(EmployeeTask).filter(Task.project_id == project_id, EmployeeTask.employee_id == employee_id).all()

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for this project and employee")

    return tasks


# Update a task by ID
@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update the fields of the task
    db_task.description = task.description
    db_task.due_date = task.due_date
    db_task.status = task.status
    db_task.owner = task.owner
    db_task.project_id = task.project_id

    db.commit()
    db.refresh(db_task)

    return db_task


# Delete a task by ID
@app.delete("/tasks/{task_id}", response_model=Task)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()

    return db_task


