import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import BSHTMLLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
import uuid
import json
from langchain.schema import Document
from datetime import datetime

class KnowledgeIndexer:
    def __init__(self, source_folder_path, target_folder_path, file_type):
        self.source_folder_path = source_folder_path
        if file_type == 'pdf':
            self.data = self.load_pdf()
        elif file_type == 'json':
            self.data = self.load_json()
        elif file_type == 'html':
            self.data = self.load_html()

        embeddings = OpenAIEmbeddings()
        # embeddings = OllamaEmbeddings(model="llama3")
        if os.path.exists(target_folder_path):
            print(f"Loading index from")
            self.collection = FAISS.load_local(
                folder_path=target_folder_path,
                embeddings=embeddings,
                allow_dangerous_deserialization=True)
        else:
            print(f"Creating a new faiss db")
            if file_type == 'json':
                self.collection = FAISS.from_documents(self.data, embeddings)
            else:
                self.collection = FAISS.from_documents(self.data[0], embeddings)
            self.collection.save_local(target_folder_path)

    def load_pdf(self):
        combined_data = []
        for filename in os.listdir(self.source_folder_path):
            if filename.endswith('.pdf'):
                file_path = os.path.join(self.source_folder_path, filename)
                with open(file_path, 'r') as file:
                    loader = PyPDFLoader(file_path)
                    pages = loader.load_and_split()
                    combined_data.append(pages)
        return combined_data

    def load_html(self):
        combined_data = []
        for filename in os.listdir(self.source_folder_path):
            if filename.endswith('.html'):
                file_path = os.path.join(self.source_folder_path, filename)
                with open(file_path, 'r') as file:
                    loader = BSHTMLLoader(file_path)
                    data = loader.load()
                    combined_data.append(data)
        return combined_data

    def load_json(self):
        combined_data = []
        for filename in os.listdir(self.source_folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.source_folder_path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    for item in data:
                        if 'create_time' in item:
                            item['create_time'] = self.convert_iso_to_custom_format(item['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                        content = json.dumps(item)
                        # print("content: " + content)
                        doc = Document(page_content=content, metadata={'timestamp': self.convert_iso_to_custom_format(item['create_time']).timestamp()})
                        combined_data.append(doc)
        return combined_data

    def convert_iso_to_custom_format(self, iso_string):
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt

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
        # filtered_results = self.filter_by_time(results, start_time, end_time)
        print("results: " + str(results))
        return results
