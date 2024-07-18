import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import BSHTMLLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
import uuid

class KnowledgeIndexer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.data = self.load_pdf()
        embeddings = OpenAIEmbeddings()
        # embeddings = OllamaEmbeddings(model="llama3")
        if os.path.exists("faiss_index"):
            print(f"Loading index from")
            self.collection = FAISS.load_local(
                folder_path="faiss_index", 
                embeddings=embeddings, 
                allow_dangerous_deserialization=True)
        else:
            print(f"Creating a new faiss db")
            self.collection = FAISS.from_documents(self.data[0], embeddings)
            self.collection.save_local("faiss_index")

    def load_pdf(self):
        combined_data = []
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.pdf'):
                file_path = os.path.join(self.folder_path, filename)
                with open(file_path, 'r') as file:
                    loader = PyPDFLoader(file_path)
                    pages = loader.load_and_split()
                    combined_data.append(pages)
        return combined_data

    def load_html(self):
        combined_data = []
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.html'):
                file_path = os.path.join(self.folder_path, filename)
                with open(file_path, 'r') as file:
                    loader = BSHTMLLoader(file_path)
                    data = loader.load()
                    combined_data.append(data)
        return combined_data

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
        results = self.collection.similarity_search(query=query, k=top_k)
        return results[0].page_content
