from typing import List
from .base_processor import BaseProcessor

class SemanticRouting(BaseProcessor):
    def process(self, query):
        if self.template_loader:
            template1 = self.template_loader.load_template('prompt_semantic_routing_1')
            template2 = self.template_loader.load_template('prompt_semantic_routing_2')
            print("Loaded semantic routing template1:", template1)
            print("Loaded semantic routing template2:", template2)
        # TODO: Add Semantic Routing
        pass
