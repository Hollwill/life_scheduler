import datetime
import uuid

import factory

from domain.task_instance.aggregate import TaskInstance, TaskStatus
from tests.factories.task_template import TaskTemplateFactory
from tests.factories.user import UserFactory


class TaskInstanceFactory(factory.Factory):
    class Meta:
        model = TaskInstance

    id = factory.LazyFunction(uuid.uuid4)

    task_template = factory.SubFactory(TaskTemplateFactory)

    user = factory.SubFactory(UserFactory)

    task_template_id = factory.SelfAttribute("task_template.id")
    user_id = factory.SelfAttribute("user.id")

    title = factory.Sequence(lambda n: f"Task Instance #{n}")

    description = factory.Faker("sentence")

    occurrence_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=1)
    )

    scheduled_at = factory.LazyFunction(lambda: datetime.time.fromisoformat("09:00"))

    created_at = factory.LazyFunction(datetime.datetime.now)

    status = TaskStatus.PENDING

    postpone_reason = None

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        kwargs.pop("task_template", None)
        kwargs.pop("user", None)

        return model_class(*args, **kwargs)
