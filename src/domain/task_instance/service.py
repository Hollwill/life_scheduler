import datetime

from domain.task_instance.aggregate import TaskInstance
from domain.task_instance.exceptions import TaskInstanceNotScheduledException
from domain.task_template.aggregate import TaskTemplate


class TaskInstanceService:
    @staticmethod
    def create_from_template(
        template: TaskTemplate,
        scheduled_day: datetime.date,
        now: datetime.datetime,
    ) -> TaskInstance:
        if not template.occurs_on(scheduled_day):
            raise TaskInstanceNotScheduledException(
                context={"scheduled_day": scheduled_day}
            )
        reminder_at = template.reminder_at(scheduled_day)

        return TaskInstance.create(
            task_template_id=template.id,
            user_id=template.user_id,
            title=template.title,
            description=template.description,
            occurrence_date=scheduled_day,
            scheduled_at=reminder_at,
            now=now,
        )
