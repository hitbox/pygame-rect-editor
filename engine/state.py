from abc import ABC
from abc import abstractmethod

class BaseState(ABC):

    def enter(self):
        "Called when entering this state"

    @abstractmethod
    def update(self):
        "Update every frame"
