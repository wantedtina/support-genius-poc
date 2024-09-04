import os
import yaml


class TemplateLoader:
    def __init__(self, templates_folder_path):
        self.templates_folder_path = templates_folder_path

    def load_template(self, template_file_name, prompt_key):
        template_path = os.path.join(self.templates_folder_path, f"{template_file_name}.yaml")
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template {template_file_name} not found at {template_path}")

        with open(os.path.join(self.templates_folder_path, template_file_name), "r") as f:
            prompt = yaml.load(f, Loader=yaml.FullLoader)
            return prompt[prompt_key]
