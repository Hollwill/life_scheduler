import datetime
import uuid
from typing import Any

from domain.task_instance.aggregate import TaskInstance
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import (
    DailyTrigger,
    MonthlyTrigger,
    OneTimeTrigger,
    Trigger,
    WeeklyTrigger,
    YearlyTrigger,
)
from domain.task_template.value_objects import (
    DayOfMonth,
    Month,
    TriggerType,
    Weekday,
)
from domain.user.aggregate import User
from infrastructure.database.models import (
    TaskInstanceModel,
    TaskTemplateModel,
    UserModel,
)


def trigger_from_dict(data: dict[str, Any]) -> Trigger:
    trigger_type = TriggerType(data["type"])

    reminder_time_raw = data.get("reminder_time")
    reminder_time: datetime.time | None = None
    if reminder_time_raw:
        reminder_time = datetime.time.fromisoformat(reminder_time_raw)

    match trigger_type:
        case TriggerType.DAILY:
            return DailyTrigger(
                id=uuid.UUID(data["id"]),
                reminder_time=reminder_time,
            )

        case TriggerType.ONE_TIME:
            return OneTimeTrigger(
                id=uuid.UUID(data["id"]),
                occurrence_date=datetime.date.fromisoformat(data["occurrence_date"]),
                reminder_time=reminder_time,
            )

        case TriggerType.WEEKLY:
            return WeeklyTrigger(
                id=uuid.UUID(data["id"]),
                weekdays=frozenset(Weekday(weekday) for weekday in data["weekdays"]),
                reminder_time=reminder_time,
            )

        case TriggerType.MONTHLY:
            return MonthlyTrigger(
                id=uuid.UUID(data["id"]),
                day_of_month=DayOfMonth(data["day_of_month"]),
                reminder_time=reminder_time,
            )

        case TriggerType.YEARLY:
            return YearlyTrigger(
                id=uuid.UUID(data["id"]),
                month=Month(data["month"]),
                day=DayOfMonth(data["day"]),
                reminder_time=reminder_time,
            )

        case _:
            raise ValueError(f"Unsupported trigger type: {trigger_type}")


def trigger_to_dict(trigger: Trigger) -> dict[str, Any]:
    reminder_time = getattr(
        trigger,
        "reminder_time",
        None,
    )

    base = {
        "id": str(trigger.id),
        "type": trigger.type.value,
        "reminder_time": (
            reminder_time.isoformat() if reminder_time is not None else None
        ),
    }

    match trigger:
        case OneTimeTrigger():
            return {
                **base,
                "occurrence_date": (trigger.occurrence_date.isoformat()),
            }
        case DailyTrigger():
            return base
        case WeeklyTrigger():
            return {
                **base,
                "weekdays": [weekday.value for weekday in trigger.weekdays],
            }
        case MonthlyTrigger():
            return {
                **base,
                "day_of_month": (trigger.day_of_month.value),
            }
        case YearlyTrigger():
            return {
                **base,
                "month": int(trigger.month),
                "day": trigger.day.value,
            }
        case _:
            raise ValueError(f"Unsupported trigger type: {trigger.type}")


def task_template_from_orm(task_template_orm: TaskTemplateModel) -> TaskTemplate:
    return TaskTemplate(
        id=task_template_orm.id,
        public_id=task_template_orm.public_id,
        user_id=task_template_orm.user_id,
        title=task_template_orm.title,
        description=task_template_orm.description,
        trigger=trigger_from_dict(task_template_orm.trigger),
        is_active=task_template_orm.is_active,
        created_at=task_template_orm.created_at,
        updated_at=task_template_orm.updated_at,
    )


def task_template_to_orm(task_template: TaskTemplate) -> TaskTemplateModel:
    return TaskTemplateModel(
        id=task_template.id,
        public_id=task_template.public_id,
        user_id=task_template.user_id,
        title=task_template.title,
        description=task_template.description,
        trigger=trigger_to_dict(task_template.trigger),
        is_active=task_template.is_active,
        created_at=task_template.created_at,
        updated_at=task_template.updated_at,
    )


def task_instance_from_orm(task_instance_orm: TaskInstanceModel) -> TaskInstance:
    return TaskInstance(
        id=task_instance_orm.id,
        public_id=task_instance_orm.public_id,
        user_id=task_instance_orm.user_id,
        task_template_id=task_instance_orm.task_template_id,
        title=task_instance_orm.title,
        description=task_instance_orm.description,
        occurrence_date=task_instance_orm.occurrence_date,
        scheduled_at=task_instance_orm.scheduled_at,
        status=task_instance_orm.status,
        created_at=task_instance_orm.created_at,
        postpone_reason=task_instance_orm.postpone_reason,
    )


def task_instance_to_orm(task_instance: TaskInstance) -> TaskInstanceModel:
    return TaskInstanceModel(
        id=task_instance.id,
        public_id=task_instance.public_id,
        user_id=task_instance.user_id,
        task_template_id=task_instance.task_template_id,
        title=task_instance.title,
        description=task_instance.description,
        occurrence_date=task_instance.occurrence_date,
        scheduled_at=task_instance.scheduled_at,
        status=task_instance.status,
        created_at=task_instance.created_at,
    )


def user_from_orm(user_orm: UserModel) -> User:
    return User(
        id=user_orm.id, telegram_user_id=user_orm.telegram_user_id, name=user_orm.name
    )


def user_to_orm(user: User) -> UserModel:
    return UserModel(id=user.id, telegram_user_id=user.telegram_user_id, name=user.name)
