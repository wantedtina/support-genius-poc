from .base_processor import BaseProcessor

class QueryTranslator(BaseProcessor):
    def process(self, query):
        if self.template_loader:
            template = self.template_loader.load_template('prompt_translator')
            print("Loaded query translator template:", template)
        # TODO: Add Query Translation 
        generated_queries = [query + " 1", query + " 2", query + " 3"] # TODO: update with the result of Query Translation 
        return generated_queries
