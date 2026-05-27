import datetime
import uuid

import factory

from domain.task_template.aggregate import TaskTemplate
from tests.factories.trigger import (
    DailyTriggerFactory,
)


class TaskTemplateFactory(factory.Factory):
    class Meta:
        model: type[TaskTemplate] = TaskTemplate

    id: factory.LazyFunction = factory.LazyFunction(uuid.uuid4)

    user_id: factory.LazyFunction = factory.LazyFunction(uuid.uuid4)

    title: factory.Sequence = factory.Sequence(lambda n: f"Task Template #{n}")

    description: factory.Faker = factory.Faker("sentence")

    trigger: factory.SubFactory = factory.SubFactory(DailyTriggerFactory)

    is_active: bool = True

    created_at: factory.LazyFunction = factory.LazyFunction(datetime.datetime.now)

    updated_at: factory.LazyAttribute = factory.LazyAttribute(
        lambda obj: obj.created_at,
    )
