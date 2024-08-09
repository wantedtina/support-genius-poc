from abc import ABC, abstractmethod

class IngestDragon(ABC):
    @abstractmethod
    def process(self, data):
        pass
