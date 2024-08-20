from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
import os

class VectorDB:
    def __init__(self, db_path, embeddings_model="openai"):
        # Set embedding by config
        if embeddings_model == "openai":
            self.embeddings = OpenAIEmbeddings()
        elif embeddings_model == "ollama":
            self.embeddings = OllamaEmbeddings(model="llama3")
        else:
            raise ValueError(f"Unsupported embeddings model: {embeddings_model}")

        self.db_path = db_path
        self.collection = self._load_or_create_db()

    def _load_or_create_db(self):
        if os.path.exists(self.db_path):
            return FAISS.load_local(
                folder_path=self.db_path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            return FAISS(embeddings=self.embeddings)

    def search(self, query, top_k=3):
        # Check if collection loaded
        if not self.collection:
            raise ValueError("The FAISS collection is not initialized.")
        
        # Check is not empty
        if not query:
            raise ValueError("The query parameter cannot be empty.")
        
        return self.collection.similarity_search(query=query, k=top_k)
