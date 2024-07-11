import json
import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders import BSHTMLLoader
# from langchain_community.document_loaders import JSONLoader
# from langchain_community.document_loaders import UnstructuredHTMLLoader
import uuid
from config import Config

class KnowledgeIndexer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        # self.data = self.load_pdf()
        self.data = []
        self.load_pdf(self.data)
        # self.load_html(self.data)
        # self.load_json(self.data)
        chroma_client = chromadb.PersistentClient(path=folder_path)
        embedding_function = OpenAIEmbeddingFunction(api_key=Config.OPENAI_API_KEY, api_base=Config.OPENAI_BASE_URL, model_name=Config.EMBED_MODEL)
        self.collection = chroma_client.get_or_create_collection(name='aa_content', embedding_function=embedding_function)
        self.populate_collection()

    def load_pdf(self, combined_data):
        combined_data = []
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.pdf'):
                file_path = os.path.join(self.folder_path, filename)
                with open(file_path, 'r') as file:
                    loader = PyPDFLoader(file_path)
                    pages = loader.load_and_split()
                    combined_data.append(pages)
        return combined_data
    
    # def load_html(self, combined_data):
    #     # combined_data = []
    #     for filename in os.listdir(self.folder_path):
    #         if filename.endswith('.mhtml'):
    #             file_path = os.path.join(self.folder_path, filename)
    #             with open(file_path, 'r') as file:
    #                 loader = UnstructuredHTMLLoader(file_path)
    #                 data = loader.load()
    #                 combined_data.append(data)
    #     return combined_data

    # def load_json(self, combined_data):
    #     # combined_data = []
    #     for filename in os.listdir(self.folder_path):
    #         if filename.endswith('.json'):
    #             file_path = os.path.join(self.folder_path, filename)
    #             with open(file_path, 'r') as file:
    #                 data = json.load(file)
    #                 combined_data.append(data)
    #     return combined_data

    def populate_collection(self):
        for doc in self.data:
            for page in doc:
                # text = f"{key}: {value}"
                self.collection.add(
                    ids=[str(uuid.uuid4())],
                    documents=[page.page_content], 
                    metadatas=[page.metadata]
                )

    def search(self, query, top_k=3):
        results = self.collection.query(query_texts=[query], n_results=top_k)
        return results["documents"][0]
