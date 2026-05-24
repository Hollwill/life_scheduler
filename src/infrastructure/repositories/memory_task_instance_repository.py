import copy
import uuid

from domain.task_instance.aggregate import TaskInstance
from domain.task_instance.repository import TaskInstanceRepository


class MemoryTaskInstanceRepository(TaskInstanceRepository):
    def __init__(self) -> None:
        self.task_instances: dict[uuid.UUID, TaskInstance] = {}

    async def get_by_id(self, task_instance_id: uuid.UUID) -> TaskInstance | None:
        instance = self.task_instances.get(task_instance_id)
        if instance is None:
            return None
        return copy.deepcopy(instance)

    async def save(self, task_instance: TaskInstance) -> None:
        self.task_instances[task_instance.id] = copy.deepcopy(task_instance)
