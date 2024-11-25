# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# Projects table
class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  # Added length to String
    description = Column(String(255))  # Added length to String
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    project_owner_id = Column(Integer)  # Added length to String

    tasks = relationship("Task", back_populates="project", cascade="all, delete")
    employees = relationship("EmployeeProject", back_populates="project", cascade="all, delete")


# Tasks table
class Task(Base):
    __tablename__ = "tasks"
    
    task_id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255))  # Added length to String
    due_date = Column(DateTime)
    status = Column(String(255))  # Added length to String
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    task_owner_id = Column(Integer)  # Added length to String
    
    project = relationship("Project", back_populates="tasks")
    employees = relationship("EmployeeTask", back_populates="task", cascade="all, delete") 


# Employee table
class Employee(Base):
    __tablename__ = "employee"
    
    employee_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))  # Added length to String
    email_id = Column(String(255))
    role = Column(String(255))  # Added length to String
    profile_image_url = Column(String(255), nullable=True)

    tasks = relationship("EmployeeTask", back_populates="employee", cascade="all, delete")
    projects = relationship("EmployeeProject", back_populates="employee", cascade="all, delete") 


# Employee-Task relation table
class EmployeeTask(Base):
    __tablename__ = "employee_task"
    
    employee_id = Column(Integer, ForeignKey("employee.employee_id"), primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id"), primary_key=True)
    
    employee = relationship("Employee", back_populates="tasks")
    task = relationship("Task", back_populates="employees")

# Employee-Project relation table
class EmployeeProject(Base):
    __tablename__ = "employee_project"

    project_id = Column(Integer, ForeignKey("projects.project_id"), primary_key=True)
    employee_id = Column(Integer, ForeignKey("employee.employee_id"), primary_key=True)

    project = relationship("Project", back_populates="employees")
    employee = relationship("Employee", back_populates="projects")
