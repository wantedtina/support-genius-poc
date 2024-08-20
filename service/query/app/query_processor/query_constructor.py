from .base_processor import BaseProcessor

class QueryConstructor(BaseProcessor):
    def process(self, query):
        if self.template_loader:
            template = self.template_loader.load_template('prompt_constructor')
            print("Loaded query constructor template:", template)
        # TODO: Add Query Constructor 
        pass
