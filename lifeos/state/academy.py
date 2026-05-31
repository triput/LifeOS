"""AcademyState — manages Specializations, Courses, Modules, LearningTasks, Certifications."""

import reflex as rx
from sqlmodel import select

from lifeos.models import Specialization, Course, Module, LearningTask, Certification
from lifeos.state.base import AppState
from lifeos.utils import model_to_dict, models_to_dicts, parse_mins


class AcademyState(AppState):
    """State for the Academy track."""

    specializations: list[dict] = []
    courses: list[dict] = []
    modules: list[dict] = []
    learning_tasks: list[dict] = []
    certifications: list[dict] = []

    selected_item: dict = {}
    selected_type: str = "specialization"
    drawer_open: bool = False

    @rx.event
    async def load_academy(self):
        """Load all academy data from the database."""
        with rx.session() as session:
            self.specializations = models_to_dicts(
                session.exec(select(Specialization)).all()
            )
            self.courses = models_to_dicts(session.exec(select(Course)).all())
            self.modules = models_to_dicts(
                session.exec(select(Module).order_by(Module.order_index)).all()
            )
            self.learning_tasks = models_to_dicts(
                session.exec(select(LearningTask)).all()
            )
            self.certifications = models_to_dicts(
                session.exec(select(Certification)).all()
            )

    @rx.event
    async def open_drawer(self, item_type: str, item_id: int):
        """Open the edit drawer for a specific academy item."""
        self.selected_type = item_type
        with rx.session() as session:
            if item_type == "specialization":
                item = session.get(Specialization, item_id)
            elif item_type == "course":
                item = session.get(Course, item_id)
            elif item_type == "module":
                item = session.get(Module, item_id)
            elif item_type == "learning_task":
                item = session.get(LearningTask, item_id)
            elif item_type == "certification":
                item = session.get(Certification, item_id)
            else:
                item = None

            self.selected_item = model_to_dict(item) if item else {}

        self.drawer_open = True

    @rx.event
    async def open_new_drawer(self, item_type: str, parent_id: int = 0):
        """Open drawer to create a new academy item."""
        self.selected_type = item_type
        base = {"id": None, "title": "", "notes": "", "notion_url": ""}
        if item_type == "specialization":
            self.selected_item = {**base, "provider": "", "status": "In Progress"}
        elif item_type == "course":
            self.selected_item = {
                **base,
                "specialization_id": parent_id,
                "provider": "",
                "status": "Planned",
            }
        elif item_type == "module":
            self.selected_item = {
                **base,
                "course_id": parent_id,
                "status": "Planned",
                "order_index": 0,
            }
        elif item_type == "learning_task":
            self.selected_item = {
                **base,
                "module_id": parent_id,
                "activity_type": "Video",
                "is_completed": False,
                "estimated_minutes": 15,
                "actual_minutes": 0,
            }
        elif item_type == "certification":
            self.selected_item = {
                **base,
                "issuer": "",
                "status": "Active",
                "pdus_required": 0,
                "pdus_completed": 0,
                "seus_required": 0,
                "seus_completed": 0,
                "issue_date": "",
                "next_renewal_date": "",
            }

        self.drawer_open = True

    @rx.event
    async def close_drawer(self):
        """Close the edit drawer."""
        self.drawer_open = False
        self.selected_item = {}

    @rx.event
    async def save_item(self, form_data: dict):
        """Upsert the selected academy item."""
        item_id = self.selected_item.get("id")
        itype = self.selected_type

        # Parse minute fields
        for field in ["estimated_minutes", "actual_minutes"]:
            if field in form_data:
                form_data[field] = parse_mins(str(form_data.get(field, 0)))

        with rx.session() as session:
            if itype == "specialization":
                if item_id:
                    item = session.get(Specialization, item_id)
                else:
                    item = Specialization(title="")
                    session.add(item)

                item.title = form_data.get("title", item.title)
                item.provider = form_data.get("provider", item.provider)
                item.status = form_data.get("status", item.status)
                item.notion_url = form_data.get("notion_url", item.notion_url)
                item.notes = form_data.get("notes", item.notes)

            elif itype == "course":
                if item_id:
                    item = session.get(Course, item_id)
                else:
                    item = Course(title="")
                    session.add(item)

                item.title = form_data.get("title", item.title)
                item.provider = form_data.get("provider", item.provider)
                item.status = form_data.get("status", item.status)
                item.notion_url = form_data.get("notion_url", item.notion_url)
                item.notes = form_data.get("notes", item.notes)
                spec_id = form_data.get("specialization_id")
                if spec_id:
                    item.specialization_id = int(spec_id)

            elif itype == "module":
                if item_id:
                    item = session.get(Module, item_id)
                else:
                    course_id = self.selected_item.get("course_id", 0)
                    item = Module(course_id=course_id, title="")
                    session.add(item)

                item.title = form_data.get("title", item.title)
                item.status = form_data.get("status", item.status)
                item.notion_url = form_data.get("notion_url", item.notion_url)
                item.notes = form_data.get("notes", item.notes)
                item.order_index = int(form_data.get("order_index", item.order_index))

            elif itype == "learning_task":
                if item_id:
                    item = session.get(LearningTask, item_id)
                else:
                    module_id = self.selected_item.get("module_id", 0)
                    item = LearningTask(module_id=module_id, title="")
                    session.add(item)

                item.title = form_data.get("title", item.title)
                item.activity_type = form_data.get("activity_type", item.activity_type)
                item.is_completed = form_data.get("is_completed", item.is_completed)
                item.estimated_minutes = form_data.get("estimated_minutes", item.estimated_minutes)
                item.actual_minutes = form_data.get("actual_minutes", item.actual_minutes)
                item.notes = form_data.get("notes", item.notes)
                item.notion_url = form_data.get("notion_url", item.notion_url)

            elif itype == "certification":
                if item_id:
                    item = session.get(Certification, item_id)
                else:
                    item = Certification(title="")
                    session.add(item)

                item.title = form_data.get("title", item.title)
                item.issuer = form_data.get("issuer", item.issuer)
                item.status = form_data.get("status", item.status)
                item.issue_date = form_data.get("issue_date") or None
                item.next_renewal_date = form_data.get("next_renewal_date") or None
                item.pdus_required = int(form_data.get("pdus_required", item.pdus_required))
                item.pdus_completed = int(form_data.get("pdus_completed", item.pdus_completed))
                item.seus_required = int(form_data.get("seus_required", item.seus_required))
                item.seus_completed = int(form_data.get("seus_completed", item.seus_completed))
                item.notes = form_data.get("notes", item.notes)
            else:
                return

            session.commit()

        self.drawer_open = False
        yield AcademyState.load_academy

    @rx.event
    async def delete_item(self):
        """Delete the currently selected academy item."""
        item_id = self.selected_item.get("id")
        itype = self.selected_type

        if not item_id:
            self.drawer_open = False
            return

        with rx.session() as session:
            if itype == "specialization":
                item = session.get(Specialization, item_id)
            elif itype == "course":
                item = session.get(Course, item_id)
            elif itype == "module":
                item = session.get(Module, item_id)
            elif itype == "learning_task":
                item = session.get(LearningTask, item_id)
            elif itype == "certification":
                item = session.get(Certification, item_id)
            else:
                item = None

            if item:
                session.delete(item)
                session.commit()

        self.drawer_open = False
        yield AcademyState.load_academy

    @rx.event
    async def toggle_learning_task(self, task_id: int):
        """Toggle a learning task's completion status."""
        with rx.session() as session:
            lt = session.get(LearningTask, task_id)
            if lt:
                lt.is_completed = not lt.is_completed
                session.commit()

        yield AcademyState.load_academy
