import uuid

import factory

from domain.task_template.entities import DailyTrigger


class DailyTriggerFactory(factory.Factory):
    class Meta:
        model: type[DailyTrigger] = DailyTrigger

    id = factory.LazyFunction(uuid.uuid4)
