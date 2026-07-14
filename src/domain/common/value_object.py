import abc


class ValueObject(abc.ABC):
    @property
    @abc.abstractmethod
    def __composite_values__(self):
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, ValueObject):
            raise NotImplementedError
        return self.__composite_values__() == other.__composite_values__()
