# ==============================================================================
# File: lifeos/models/learning.py
# Description: PostgreSQL schema for the Academy domain.
# Component: Data Layer
# Version: 1.0 (Gold Master)
# ==============================================================================

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from lifeos.models.mixins import TimeTrackableItem

class LifeSpecialization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    provider: str
    status: str
    progress: int = 0
    
    courses: List["LifeCourse"] = Relationship(back_populates="specialization")

class LifeCourse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    specialization_id: Optional[int] = Field(default=None, foreign_key="lifespecialization.id")
    title: str
    provider: str
    status: str
    progress: int = 0
    
    specialization: Optional[LifeSpecialization] = Relationship(back_populates="courses")
    modules: List["LifeModule"] = Relationship(back_populates="course")

class LifeModule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: Optional[int] = Field(default=None, foreign_key="lifecourse.id")
    title: str
    status: str
    
    course: Optional[LifeCourse] = Relationship(back_populates="modules")
    activities: List["LifeActivity"] = Relationship(back_populates="module")

class LifeActivity(TimeTrackableItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    module_id: Optional[int] = Field(default=None, foreign_key="lifemodule.id")
    title: str
    activity_type: str
    
    module: Optional[LifeModule] = Relationship(back_populates="activities")

class LifeCertification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    issuer: str
    issue_date: str
    expiration_date: Optional[str] = None
    status: str
    pdus_required: int = 0
    pdus_earned: int = 0