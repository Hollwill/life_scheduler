from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Integer,
    String,
    Table,
    UniqueConstraint,
    event,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import registry

from domain.task_instance.aggregate import TaskInstance, TaskStatus
from domain.task_template.aggregate import TaskTemplate
from domain.user.aggregate import User
from infrastructure.database.metadata import metadata
from infrastructure.database.outbox import OutboxModel
from infrastructure.database.types import TimeZoneType, TriggerType

task_template_table = Table(
    "task_template",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("public_id", String(8), nullable=False, unique=True),
    Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
    Column("title", String(255), nullable=False),
    Column("description", String, nullable=True),
    Column("trigger", TriggerType, nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

task_instance_table = Table(
    "task_instance",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("public_id", String(8), nullable=False, unique=True),
    Column("task_template_id", UUID(as_uuid=True), nullable=True, index=True),
    Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
    Column("title", String(255), nullable=False),
    Column("description", String, nullable=True),
    Column("occurrence_date", Date, nullable=False, index=True),
    Column("scheduled_at", DateTime(timezone=True), nullable=True, index=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("status", Enum(TaskStatus), nullable=False),
    Column("postpone_reason", String, nullable=True),
    Column("reminded_at", DateTime(timezone=True), nullable=True),
    UniqueConstraint(
        "task_template_id",
        "occurrence_date",
        name="uq_task_template_per_day",
    ),
)

user_table = Table(
    "user",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("telegram_user_id", Integer, nullable=False, unique=True),
    Column("timezone", TimeZoneType, nullable=False),
    Column("name", String(255), nullable=True),
)

outbox_table = Table(
    "outbox",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("event_type", String(255), nullable=False),
    Column("payload", JSONB, nullable=False),
    Column(
        "created_at", DateTime(timezone=True), nullable=False, server_default=func.now()
    ),
    Column("processed_at", DateTime(timezone=True), nullable=True),
)

mapper_registry = registry(metadata=metadata)


mapper_registry.map_imperatively(
    TaskTemplate,
    task_template_table,
)

mapper_registry.map_imperatively(
    TaskInstance,
    task_instance_table,
)

mapper_registry.map_imperatively(
    User,
    user_table,
)


mapper_registry.map_imperatively(
    OutboxModel,
    outbox_table,
)


@event.listens_for(TaskInstance, "load")
def task_instance_loaded(target, context):
    target._events = []


@event.listens_for(TaskTemplate, "load")
def task_template_loaded(target, context):
    target._events = []


@event.listens_for(User, "load")
def user_loaded(target, context):
    target._events = []
