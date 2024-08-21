from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="llama3")
new_vector_store = FAISS.load_local(
                folder_path="faiss_index/serviceNow",
                embeddings=embeddings,
                allow_dangerous_deserialization=True)

docs = new_vector_store.similarity_search("YNB01233581")

print(docs)