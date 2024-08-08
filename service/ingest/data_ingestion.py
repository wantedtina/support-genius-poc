from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import uuid
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

# Database configuration
db_url = 'postgresql://user:password@localhost:5432/yourdatabase'
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
metadata = MetaData()

# Define the documents table
documents_table = Table('documents', metadata,
                        Column('id', String, primary_key=True),
                        Column('content', String),
                        Column('create_time', DateTime))

# Create the table if it doesn't exist
metadata.create_all(engine)

# FAISS configuration
faiss_index_path = 'faiss_index/knowledge_index'
embeddings = OllamaEmbeddings(model="llama3")
if os.path.exists(faiss_index_path):
    collection = FAISS.load_local(
        folder_path=faiss_index_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )
else:
    collection = FAISS([], embeddings)
    collection.save_local(faiss_index_path)

def fetch_data_from_sources():
    # Implement your data fetching logic here
    return [
        {'id': str(uuid.uuid4()), 'content': 'Sample document 1', 'create_time': datetime.utcnow()},
        {'id': str(uuid.uuid4()), 'content': 'Sample document 2', 'create_time': datetime.utcnow()},
    ]

def ingest_data_into_db():
    session = Session()
    try:
        data = fetch_data_from_sources()
        for item in data:
            ins = documents_table.insert().values(
                id=item['id'],
                content=item['content'],
                create_time=item['create_time']
            )
            session.execute(ins)

            # Add to FAISS
            doc = Document(page_content=item['content'], metadata={'timestamp': item['create_time']})
            collection.add_documents([doc])

        session.commit()
        collection.save_local(faiss_index_path)
        print(f'Ingested {len(data)} documents into the database and FAISS.')
    except Exception as e:
        session.rollback()
        print(f'Error ingesting data: {e}')
    finally:
        session.close()

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(ingest_data_into_db, 'interval', hours=1)
    print('Starting data ingestion service...')
    ingest_data_into_db()  # Initial run
    scheduler.start()
