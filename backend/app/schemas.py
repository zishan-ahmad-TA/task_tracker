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
    member_ids: Optional[List[int]] = []

class EmployeeBriefResponse(BaseModel):
    employee_id: int
    name: str


class UpdateRoleRequest(BaseModel):
    new_role: str
    employee_id: int


class ProjectUpdate(ProjectBase):
    pass
    #project_status: str 
    #project_owner_id: int


class ProjectResponse(BaseModel):
    project_name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    project_id: int
    project_owner_id: int
    project_owner_name: str
    project_status: str
    managers: List[EmployeeBriefResponse]
    members: List[EmployeeBriefResponse]

    class Config:
        orm_mode = True

class ProjectComplete(BaseModel):
    project_id: int
    project_status: str

class ProjectCreate(BaseModel):
    project_name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
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
    name: str
    description: str
    due_date: datetime
    employee_ids: List[int]

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    task_id: int
    project_id: int
    task_status: str
    task_owner_id: int
    task_owner_name: str

    class Config:
        orm_mode = True

# Task response model for individual tasks
class TaskResponse(BaseModel):
    task_id: int
    name: str
    description: str
    due_date: datetime
    status: str
    task_owner_id: int
    task_owner_name: str
    #employee_names: List[str]  # Names of employees assigned to the task
    members: List[EmployeeBriefResponse]

    class Config:
        orm_mode = True

# Response model for the list of tasks
class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    task_count: int

# Model for updating a task
class TaskUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    due_date: datetime
    #task_status: str
    employee_ids: List[int]



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


class MemberResponse(BaseModel):
    employee_id: int
    name: str
    email_id: str
    role: str

    class Config:
        from_attributes = True

class MemberListResponse(BaseModel):
    members: List[MemberResponse]
    member_count: int

class EmployeeResponse(BaseModel):
    employee_id: int
    name: str
    role: str

    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    employees: List[EmployeeResponse]
    employee_count: int
 

# Response model for a single project
class EmployeeProjectResponse(BaseModel):
    project_id: int
    project_name: str
    description: str
    start_date: datetime
    end_date: datetime
    project_status: str
    project_owner_id: int
    project_owner_name: str

    class Config:
        orm_mode = True

# Response model for list of projects assigned to an employee
class EmployeeProjectsListResponse(BaseModel):
    projects: List[EmployeeProjectResponse]
    project_count: int

    # Response model for a single task
class EmployeeTaskResponse(BaseModel):
    task_id: int
    task_name: str
    description: str
    due_date: datetime
    task_status: str
    project_id: int
    project_name: str
    task_owner_id: int
    task_owner_name: str

    class Config:
        orm_mode = True

# Response model for list of tasks assigned to an employee
class EmployeeTasksListResponse(BaseModel):
    tasks: List[EmployeeTaskResponse]
    task_count: int



