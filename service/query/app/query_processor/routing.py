from .base_processor import BaseProcessor

class Routing(BaseProcessor):
    def construct(self, template, knowledge, question):
        return template.format(knowledge=knowledge, question=question)
