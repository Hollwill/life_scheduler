class Entity[TId]:
    def __init__(self, id: TId):
        self._id = id

    _id: TId

    @property
    def id(self) -> TId:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id
