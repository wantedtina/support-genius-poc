from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    def __init__(self, template_loader=None, llm=None):
        self.template_loader = template_loader
        self.llm = llm
    @abstractmethod
    def process(self, results: list[list]):
        pass
