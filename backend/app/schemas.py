# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# Pydantic model for Project
class ProjectBase(BaseModel):
    project_name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    manager_ids: Optional[List[int]] = []
    employee_ids: Optional[List[int]] = []



class ProjectUpdate(ProjectBase):
    project_status: str 
    project_owner_id: int


class ProjectResponse(ProjectBase):
    project_id: int
    project_owner_id: int
    project_owner_name: str
    project_status: str

    class Config:
        orm_mode = True

class ProjectUpdateResponse(ProjectBase):
    project_owner_name: str

    class Config:
        orm_mode = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    project_count: int

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

class ManagerResponse(BaseModel):
    employee_id: int
    name: str
    email_id: str
    role: str

    class Config:
        from_attributes = True

class ManagerListResponse(BaseModel):
    managers: List[ManagerResponse]
    manager_count: int

class EmployeeResponse(BaseModel):
    employee_id: int
    name: str
    role: str

    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    employees: List[EmployeeResponse]
    employee_count: int

class RoleUpdateRequest(BaseModel):
    new_role: str  



