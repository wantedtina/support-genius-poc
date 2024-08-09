from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
import os

class VectorDB:
    def __init__(self, target_folder_path, embeddings_model="llama3"):
        self.target_folder_path = target_folder_path
        self.embeddings = OllamaEmbeddings(model=embeddings_model)
        if os.path.exists(target_folder_path):
            self.collection = FAISS.load_local(
                folder_path=target_folder_path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            self.collection = None

    def store(self, documents):
        if self.collection is None:
            self.collection = FAISS.from_documents(documents, self.embeddings)
            self.collection.save_local(self.target_folder_path)
        else:
            self.collection.add_documents(documents)

    def search(self, query, top_k=3):
        return self.collection.similarity_search(query=query, k=top_k)
