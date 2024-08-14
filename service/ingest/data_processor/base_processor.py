from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    @abstractmethod
    def process(self, data):
        pass
