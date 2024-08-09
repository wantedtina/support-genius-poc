import os
import yaml

class TemplateLoader:
    def __init__(self, templates_folder_path):
        self.templates_folder_path = templates_folder_path

    def load_template(self, template_name):
        template_path = os.path.join(self.templates_folder_path, f"{template_name}.yaml")
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template {template_name} not found at {template_path}")
        
        with open(template_path, 'r') as file:
            return yaml.load(file, Loader=yaml.FullLoader)
