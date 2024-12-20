from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


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

class TaskResponse(BaseModel):
    task_id: int
    name: str
    description: str
    due_date: datetime
    status: str
    task_owner_id: int
    task_owner_name: str
    #employee_names: List[str] 
    members: List[EmployeeBriefResponse]

    class Config:
        orm_mode = True

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    task_count: int

class TaskUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    due_date: datetime
    #task_status: str
    employee_ids: List[int]

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

class EmployeeProjectsListResponse(BaseModel):
    projects: List[EmployeeProjectResponse]
    project_count: int

class EmployeeTaskResponse(BaseModel):
    task_id: int
    name: str
    description: str
    due_date: datetime
    status: str
    project_id: int
    project_name: str
    task_owner_id: int
    task_owner_name: str

    class Config:
        orm_mode = True

class EmployeeTasksListResponse(BaseModel):
    tasks: List[EmployeeTaskResponse]
    task_count: int

class UpdateTaskStatusRequest(BaseModel):
    task_id: int
    new_status: str


