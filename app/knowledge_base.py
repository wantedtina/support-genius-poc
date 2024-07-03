import json
import os

class KnowledgeBase:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.data = self.load_data()

    def load_data(self):
        combined_data = {}
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.folder_path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    combined_data[filename] = data
        return combined_data

    def get_knowledge_text(self):
        knowledge_text = ""
        for key, value in self.data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    knowledge_text += f"{sub_key}: {sub_value}\n"
            else:
                knowledge_text += f"{key}: {value}\n"
        return knowledge_text

    def search(self, query):
        for key, value in self.data.items():
            if key.lower() in query.lower():
                return value
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key.lower() in query.lower():
                        return sub_value
        return None
