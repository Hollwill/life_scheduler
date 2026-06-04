import datetime
import uuid

import factory

from domain.common.utils import generate_public_id
from domain.task_template.aggregate import TaskTemplate
from tests.factories.trigger import (
    DailyTriggerFactory,
)


class TaskTemplateFactory(factory.Factory):
    class Meta:
        model = TaskTemplate

    id = factory.LazyFunction(uuid.uuid4)

    public_id = factory.LazyFunction(generate_public_id)

    user_id = factory.LazyFunction(uuid.uuid4)

    title = factory.Sequence(lambda n: f"Task Template #{n}")

    description = factory.Faker("sentence")

    trigger = factory.SubFactory(DailyTriggerFactory)

    is_active = True

    created_at = factory.LazyFunction(datetime.datetime.now)

    updated_at = factory.LazyAttribute(
        lambda obj: obj.created_at,
    )
