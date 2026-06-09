import typing

from sqlalchemy import (
    TypeDecorator,
)
from sqlalchemy.dialects.postgresql import JSONB

from domain.task_template.entities import Trigger
from infrastructure.database.trigger_mapper import TriggerMapper


class TriggerType(TypeDecorator):
    impl = JSONB

    def process_bind_param(self, value: Trigger, dialect):
        return TriggerMapper.trigger_to_dict(value)

    def process_result_value(self, value: dict[str, typing.Any], dialect):
        return TriggerMapper.trigger_from_dict(value)
