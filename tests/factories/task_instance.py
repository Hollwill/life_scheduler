import datetime
import uuid

import factory

from domain.common.utils import generate_public_id
from domain.task_instance.aggregate import TaskInstance, TaskStatus


class TaskInstanceFactory(factory.Factory):
    class Meta:
        model = TaskInstance

    id = factory.LazyFunction(uuid.uuid4)

    public_id = factory.LazyFunction(generate_public_id)

    task_template_id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)

    title = factory.Sequence(lambda n: f"Task Instance #{n}")

    description = factory.Faker("sentence")

    occurrence_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=1)
    )

    scheduled_at = factory.LazyFunction(
        lambda: datetime.datetime.combine(
            datetime.date.today() + datetime.timedelta(days=1),
            datetime.time.fromisoformat("09:00"),
        )
    )

    created_at = factory.LazyFunction(datetime.datetime.now)

    status = TaskStatus.PENDING

    postpone_reason = None
