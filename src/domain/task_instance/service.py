import datetime

from domain.task_instance.aggregate import TaskInstance
from domain.task_template.aggregate import TaskTemplate


class TaskGenerationService:
    @staticmethod
    def generate_from_template(
        template: TaskTemplate,
        scheduled_at: datetime.datetime | None,
        day: datetime.date,
        now: datetime.datetime,
    ) -> TaskInstance | None:
        if not template.is_active:
            return None
        if not template.occurs_on(day):
            return None

        return TaskInstance.create(
            task_template_id=template.id,
            user_id=template.user_id,
            title=template.title,
            description=template.description,
            occurrence_date=day,
            scheduled_at=scheduled_at,
            now=now,
        )
