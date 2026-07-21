import typing

from domain.task_instance.aggregate import TaskInstance


class TaskInstancesFormatter:
    @classmethod
    def format(cls, task_instances: typing.Iterable[TaskInstance]) -> str:
        header = "📋 Tasks"

        task_instances = list(task_instances)

        if not task_instances:
            return f"{header}\n\nNo tasks today."

        rendered = [
            cls._render_task_instance(task_instance) for task_instance in task_instances
        ]

        return "\n\n".join((header, *rendered))

    @classmethod
    def _render_task_instance(cls, task_instance: TaskInstance) -> str:
        parts = [
            f"#{str(task_instance.public_id)}",
            task_instance.title,
        ]

        if task_instance.description:
            parts.append(f"📝 {task_instance.description}")

        parts.append(f"📅 {task_instance.occurrence_date.isoformat()}")

        if task_instance.scheduled_at:
            parts.append(
                f"⏰ {task_instance.scheduled_at.time().isoformat(timespec='minutes')}"
            )

        parts.append(f"✅ {task_instance.status}")

        return "\n".join(parts)
