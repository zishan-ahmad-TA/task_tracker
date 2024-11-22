# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Pydantic model for Project
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    owner: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    project_id: int

    class Config:
        orm_mode = True  # This is needed for FastAPI to convert SQLAlchemy models into Pydantic models


# Pydantic model for Task
class TaskBase(BaseModel):
    description: str
    due_date: datetime
    status: str
    owner: str

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    task_id: int
    project_id: int

    class Config:
        orm_mode = True


# Pydantic model for Employee
class EmployeeBase(BaseModel):
    name: str
    role: str

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    employee_id: int

    class Config:
        orm_mode = True
