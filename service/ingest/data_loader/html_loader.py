from langchain_community.document_loaders import BSHTMLLoader
import os

class HtmlLoader:
    def __init__(self, source_folder_path):
        self.source_folder_path = source_folder_path

    def load_data(self):
        combined_data = []
        for filename in os.listdir(self.source_folder_path):
            if filename.endswith('.html'):
                file_path = os.path.join(self.source_folder_path, filename)
                with open(file_path, 'r') as file:
                    loader = BSHTMLLoader(file_path)
                    data = loader.load()
                    combined_data.append(data)
        return combined_data
