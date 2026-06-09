class Entity[TId]:
    def __init__(self, id: TId):
        self.id = id

    id: TId

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id
