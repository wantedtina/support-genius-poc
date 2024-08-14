from langchain_community.document_loaders import PyPDFLoader
import os

class PdfLoader:
    def __init__(self, source_folder_path):
        self.source_folder_path = source_folder_path

    def load_data(self):
        combined_data = []
        for filename in os.listdir(self.source_folder_path):
            if filename.endswith('.pdf'):
                file_path = os.path.join(self.source_folder_path, filename)
                with open(file_path, 'r') as file:
                    loader = PyPDFLoader(file_path)
                    pages = loader.load_and_split()
                    combined_data.append(pages)
        return combined_data
