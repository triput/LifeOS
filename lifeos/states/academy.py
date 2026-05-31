# ==============================================================================
# File: lifeos/states/academy.py
# Description: State management for professional development, coursework, and PDUs.
# Component: State Management Layer
# Version: 1.1 (Gold Master)
# Created: 2026-05-04
# ==============================================================================

import reflex as rx
from sqlmodel import select
from pydantic import BaseModel
from typing import Optional, List


from lifeos.state import State
from lifeos.models.learning import LifeSpecialization, LifeCourse, LifeCertification 


# --- 1. COURSEWORK HIERARCHY SCHEMAS ---

class LearningActivity(BaseModel):
    """The smallest unit of learning (avoids namespace collision with Agile Tasks)."""
    id: str
    title: str
    activity_type: str  # e.g., "Video", "Quiz", "Lab", "Reading"
    status: str         # e.g., "Not Started", "In Progress", "Completed"
    duration_minutes: int

class CourseModule(BaseModel):
    """A collection of activities."""
    id: str
    title: str
    status: str
    activities: List[LearningActivity] = []

class CourseItem(BaseModel):
    """A standalone course, or a component of a Specialization."""
    id: str
    title: str
    provider: str  
    status: str    
    progress: int  
    modules: List[CourseModule] = []

class SpecializationItem(BaseModel):
    """The highest level: A curated track of multiple courses."""
    id: str
    title: str
    provider: str
    status: str
    progress: int
    courses: List[CourseItem] = []

# --- 2. CERTIFICATION & PDU SCHEMA ---

class CertItem(BaseModel):
    """Tracks active certifications and their continuing education requirements."""
    id: str
    title: str
    issuer: str
    issue_date: str
    expiration_date: Optional[str]
    status: str    
    pdus_required: int = 0  # NEW: The target goal for renewal
    pdus_earned: int = 0    # NEW: Current ledger balance

# --- STATE ENGINE ---

class AcademyState(State):
    """Manages the lifecycle of coursework, specializations, and PDUs."""
    
    specialization_list: List[SpecializationItem] = []
    standalone_course_list: List[CourseItem] = []
    cert_list: List[CertItem] = []
    
    # --- TRACK CONSTRUCTOR FORM STATE ---
    track_modal_open: bool = False
    new_track_title: str = ""
    new_track_provider: str = ""
    new_track_type: str = "Specialization"
    new_track_status: str = "Planned"
    
    # --- MANUAL SETTERS (Defensive Architecture) ---
    def set_track_modal_open(self, value: bool):
        self.track_modal_open = value

    def set_new_track_title(self, value: str):
        self.new_track_title = value

    def set_new_track_provider(self, value: str):
        self.new_track_provider = value

    def set_new_track_type(self, value: str):
        self.new_track_type = value

    def set_new_track_status(self, value: str):
        self.new_track_status = value
    

    def toggle_track_modal(self):
        """Opens/closes the modal and clears the form on exit."""
        self.track_modal_open = not self.track_modal_open
        if not self.track_modal_open:
            self.new_track_title = ""
            self.new_track_provider = ""
            self.new_track_status = "Planned"

    def submit_new_track(self):
        """Writes the form data to PostgreSQL and refreshes the UI."""
        # 1. Basic validation (don't save empty tracks)
        if not self.new_track_title.strip() or not self.new_track_provider.strip():
            return 

        # 2. Write to the database
        with rx.session() as session:
            if self.new_track_type == "Specialization":
                new_track = LifeSpecialization(
                    title=self.new_track_title,
                    provider=self.new_track_provider,
                    status=self.new_track_status,
                    progress=0
                )
            else:
                new_track = LifeCourse(
                    title=self.new_track_title,
                    provider=self.new_track_provider,
                    status=self.new_track_status,
                    progress=0
                )
            session.add(new_track)
            session.commit()

        # 3. Reload the live data and close the modal
        self.load_academy_data()
        self.toggle_track_modal()
    
    

    def load_academy_data(self):
        """Fetches and translates LIVE PostgreSQL data for the UI dashboard."""
        with rx.session() as session:
            # 1. Load Certifications
            db_certs = session.exec(select(LifeCertification)).all()
            self.cert_list = [
                CertItem(
                    id=str(c.id), title=c.title, issuer=c.issuer, issue_date=c.issue_date,
                    expiration_date=c.expiration_date, status=c.status,
                    pdus_required=c.pdus_required, pdus_earned=c.pdus_earned
                ) for c in db_certs
            ]

            # 2. Load Specializations (Nested Unpacking)
            db_specs = session.exec(select(LifeSpecialization)).all()
            spec_payload = []
            for spec in db_specs:
                course_payload = []
                for course in spec.courses:
                    module_payload = []
                    for mod in course.modules:
                        act_payload = [
                            LearningActivity(
                                id=str(a.id), title=a.title, activity_type=a.activity_type, 
                                status=a.status, 
                                duration_minutes=a.estimated_minutes # <-- BOMB DEFUSED!
                            ) for a in mod.activities
                        ]
                        module_payload.append(CourseModule(id=str(mod.id), title=mod.title, status=mod.status, activities=act_payload))
                    
                    course_payload.append(CourseItem(
                        id=str(course.id), title=course.title, provider=course.provider,
                        status=course.status, progress=course.progress, modules=module_payload
                    ))
                
                spec_payload.append(SpecializationItem(
                    id=str(spec.id), title=spec.title, provider=spec.provider,
                    status=spec.status, progress=spec.progress, courses=course_payload
                ))
            self.specialization_list = spec_payload

            # 3. Load Standalone Courses (FIXED: Unpacking nested children!)
            db_courses = session.exec(select(LifeCourse).where(LifeCourse.specialization_id == None)).all()
            standalone_payload = []
            for course in db_courses:
                module_payload = []
                for mod in course.modules:
                    act_payload = [
                        LearningActivity(
                            id=str(a.id), title=a.title, activity_type=a.activity_type, 
                            status=a.status, 
                            duration_minutes=a.estimated_minutes # <-- BOMB DEFUSED!
                        ) for a in mod.activities
                    ]
                    module_payload.append(CourseModule(id=str(mod.id), title=mod.title, status=mod.status, activities=act_payload))
                
                standalone_payload.append(CourseItem(
                    id=str(course.id), title=course.title, provider=course.provider, 
                    status=course.status, progress=course.progress, modules=module_payload
                ))
            self.standalone_course_list = standalone_payload

    # ==========================================
    # --- MODULE CONSTRUCTOR STATE ---
    # ==========================================
    module_modal_open: bool = False
    active_course_id: str = ""
    new_module_title: str = ""

    def set_new_module_title(self, value: str): self.new_module_title = value

    def open_module_modal(self, course_id: str):
        self.active_course_id = course_id
        self.new_module_title = ""
        self.module_modal_open = True

    def close_module_modal(self):
        self.module_modal_open = False

    def submit_new_module(self):
        if not self.new_module_title.strip() or not self.active_course_id:
            return
            
        with rx.session() as session:
            # We import LifeModule locally here to avoid any circular import issues at the top
            from lifeos.models.learning import LifeModule
            new_mod = LifeModule(
                title=self.new_module_title, 
                status="Not Started", 
                course_id=int(''.join(filter(str.isdigit, str(self.active_course_id))))
            )
            session.add(new_mod)
            session.commit()
            
        self.load_academy_data()
        self.close_module_modal()

    # ==========================================
    # --- ACTIVITY CONSTRUCTOR STATE ---
    # ==========================================
    activity_modal_open: bool = False
    active_module_id: str = ""
    new_activity_title: str = ""
    new_activity_type: str = "Video"
    new_activity_duration: str = "15" # String for input field, we will cast to int

    def set_new_activity_title(self, value: str): self.new_activity_title = value
    def set_new_activity_type(self, value: str): self.new_activity_type = value
    def set_new_activity_duration(self, value: str): self.new_activity_duration = value

    def open_activity_modal(self, module_id: str):
        self.active_module_id = module_id
        self.new_activity_title = ""
        self.new_activity_duration = "15"
        self.activity_modal_open = True

    def close_activity_modal(self):
        self.activity_modal_open = False

    def submit_new_activity(self):
        if not self.new_activity_title.strip() or not self.active_module_id:
            return
            
        with rx.session() as session:
            from lifeos.models.learning import LifeActivity
            # Notice we use 'estimated_minutes' now because of our awesome Mixin!
            new_act = LifeActivity(
                title=self.new_activity_title,
                activity_type=self.new_activity_type,
                status="Not Started",
                estimated_minutes=int(self.new_activity_duration) if self.new_activity_duration.isdigit() else 0,
                module_id=int(''.join(filter(str.isdigit, str(self.active_module_id))))
            )
            session.add(new_act)
            session.commit()
            
        self.load_academy_data()
        self.close_activity_modal()
        # ==========================================
    # --- NESTED COURSE CONSTRUCTOR STATE ---
    # ==========================================
    course_modal_open: bool = False
    active_specialization_id: str = ""
    new_nested_course_title: str = ""
    new_nested_course_provider: str = ""

    def set_new_nested_course_title(self, value: str): self.new_nested_course_title = value
    def set_new_nested_course_provider(self, value: str): self.new_nested_course_provider = value

    def open_course_modal(self, spec_id: str):
        self.active_specialization_id = str(spec_id)
        self.new_nested_course_title = ""
        self.new_nested_course_provider = ""
        self.course_modal_open = True

    def close_course_modal(self):
        self.course_modal_open = False

    def submit_new_nested_course(self):
        if not self.new_nested_course_title.strip() or not self.active_specialization_id:
            return
            
        # SAFELY strip letters to prevent the 'c1' crash!
        clean_spec_id = int(''.join(filter(str.isdigit, self.active_specialization_id)))
        
        with rx.session() as session:
            from lifeos.models.learning import LifeCourse
            new_course = LifeCourse(
                title=self.new_nested_course_title,
                provider=self.new_nested_course_provider,
                status="Planned",
                specialization_id=clean_spec_id
            )
            session.add(new_course)
            session.commit()
            
        self.load_academy_data()
        self.close_course_modal()


        
        # ---------------------------------------------------------
        # Dummy Data to build the UI against
        # ---------------------------------------------------------
        
        self.specialization_list = [
            SpecializationItem(
                id="1",
                title="Agentic AI Architectures",
                provider="DeepLearning.AI",
                status="In Progress",
                progress=30,
                courses=[
                    CourseItem(
                        id="c1", 
                        title="ReAct & Multi-Agent Orchestration", 
                        provider="DeepLearning.AI", 
                        status="In Progress", 
                        progress=65,
                        modules=[
                            CourseModule(
                                id="m1",
                                title="Module 1: Memory Graphs",
                                status="Completed",
                                activities=[
                                    LearningActivity(id="a1", title="Intro to Memory", activity_type="Video", status="Completed", duration_minutes=15)
                                ]
                            )
                        ]
                    )
                ]
            )
        ]

        self.standalone_course_list = [
            CourseItem(
                id="c2", 
                title="Advanced Earned Value Management", 
                provider="PMI", 
                status="Planned", 
                progress=0,
                modules=[]
            )
        ]
        
        self.cert_list = [
            CertItem(
                id="1", 
                title="Project Management Professional (PMP)", 
                issuer="Project Management Institute", 
                issue_date="Oct 2023", 
                expiration_date="Oct 2026", 
                status="Active",
                pdus_required=60,
                pdus_earned=42
            ),
            CertItem(
                id="2", 
                title="Certified ScrumMaster (CSM)", 
                issuer="Scrum Alliance", 
                issue_date="Jan 2022", 
                expiration_date="Jan 2024", 
                status="Expired",
                pdus_required=20,
                pdus_earned=0
            )
        ]
        
