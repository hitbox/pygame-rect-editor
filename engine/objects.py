from abc import ABC
from abc import abstractmethod

class BaseObject(ABC):

    @abstractmethod
    def update(self):
        pass
