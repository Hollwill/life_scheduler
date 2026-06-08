import uuid

from domain.task_instance.aggregate import TaskInstance
from domain.task_template.aggregate import TaskTemplate
from domain.user.aggregate import User


class MemoryDatabase:
    def __init__(self):
        self.task_instances: dict[uuid.UUID, TaskInstance] = {}
        self.task_templates: dict[uuid.UUID, TaskTemplate] = {}
        self.users: dict[uuid.UUID, User] = {}
