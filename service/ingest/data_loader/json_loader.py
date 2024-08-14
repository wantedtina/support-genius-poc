import json
import os

class JsonLoader:
    def __init__(self, source_folder_path):
        self.source_folder_path = source_folder_path

    def load_data(self):
        combined_data = []
        for filename in os.listdir(self.source_folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.source_folder_path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    combined_data.extend(data)
        return combined_data
