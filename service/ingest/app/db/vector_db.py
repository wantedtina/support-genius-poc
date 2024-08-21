from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
import os
from uuid import uuid4
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore

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
        if os.path.exists(self.db_path):
            self.collection = FAISS.load_local(
                folder_path=self.db_path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            texts = ["FAISS is an important library", "LangChain supports FAISS"]
            self.collection = FAISS.from_texts(texts, self.embeddings)
            # index = faiss.IndexFlatL2(len(self.embeddings.embed_query("hello world")))
            # self.collection = FAISS(
            #     embedding_function=self.embeddings,
            #     index=index,
            #     docstore=InMemoryDocstore(),
            #     index_to_docstore_id={},
            # )
            self.collection.save_local(self.db_path)

    def _load_or_create_db(self):
        if os.path.exists(self.db_path):
            return FAISS.load_local(
                folder_path=self.db_path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            return FAISS(embeddings=self.embeddings)
        
    def store(self, docs):
        uuids = [str(uuid4()) for _ in range(len(docs))]
        self.collection = FAISS.add_documents(docs, uuids)
        # self.collection = FAISS.from_documents(docs, self.embeddings)

    def search(self, query, top_k=3):
        # Check if collection loaded
        if not self.collection:
            raise ValueError("The FAISS collection is not initialized.")
        
        # Check is not empty
        if not query:
            raise ValueError("The query parameter cannot be empty.")
        
        return self.collection.similarity_search(query=query, k=top_k)
