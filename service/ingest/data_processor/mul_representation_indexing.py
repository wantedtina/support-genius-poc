from abc import ABC, abstractmethod

class MulReprenIndexing(ABC):
    @abstractmethod
    def process(self, data):
        pass
