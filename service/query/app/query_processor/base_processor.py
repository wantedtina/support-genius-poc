from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    @abstractmethod
    def construct(self, template, knowledge, question):
        pass
