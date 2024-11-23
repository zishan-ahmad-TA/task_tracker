# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# Pydantic model for Project
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    project_owner: str
    employee_ids: List[int]  # List of employee IDs to assign to the project

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
    task_owner: str
    status: str
    employee_ids: List[int]

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
    email_id: str
    role: str

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    employee_id: int

    class Config:
        orm_mode = True
