import yaml
import json

def load_config(path):
    if path.endswith('.yaml') or path.endswith('.yml'):
        with open(path, 'r', encoding='utf-8') as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    else:
        raise ValueError("Unsupported configuration file format. Please use YAML or JSON.")

