from flask import Blueprint, request, jsonify
from .utils.config_loader import load_config
from .data_loader import HtmlLoader, JsonLoader, PdfLoader
from .data_processor import HtmlProcessor, JsonProcessor, PdfProcessor
from .db.vector_db import VectorDB
from .db.es_db import EsDB
from .db.graph_db import GraphDB
from .db.sql_db import SqlDB
from .knowledge_indexer import KnowledgeIndexer

main = Blueprint('main', __name__)

# Load Config
config = load_config('app/config/channel_config.yaml')

knowledge_indexer_sn = KnowledgeIndexer('data', 'faiss_index/serviceNow', 'json')

# Load Data Loaders
data_loaders = {
    "json_loader": JsonLoader,
    "pdf_loader": PdfLoader,
    "html_loader": HtmlLoader,
    # Add other loaders as needed
}

# Load Data Processors
data_processors = {
    "json_processor": JsonProcessor,
    "html_processor": HtmlProcessor,
    "pdf_processor": PdfProcessor,
    # Add other processors as needed
}

# Load Vector DB class
db_classes = {
    "vector": VectorDB,
    "sql": SqlDB,
    "es": EsDB,
    "graph": GraphDB
}

@main.route('/ingest/<channel>', methods=['POST'])
def ingest_data(channel):
    try:
        # Get the channel configuration
        channel_config = config['channels'].get(channel)
        if not channel_config:
            return jsonify({'response': "Invalid channel"})

        # Get the raw data from the request
        raw_data = request.json
        if not raw_data:
            return jsonify({'response': "No data provided"}), 400

        # Step 1: Load the data using the appropriate loader
        # loader_name = channel_config['data_loader']
        # loader_class = data_loaders.get(loader_name)
        # if not loader_class:
        #     return jsonify({'response': f"Unsupported data loader {loader_name}"}), 400

        # loader = loader_class(source_data=raw_data)
        # loaded_data = loader.load_data()

        # Step 2: Process the data using the configured processors
        processed_data = raw_data
        for processor_config in channel_config['data_processor']:
            processor_name = processor_config['name']
            processor_params = processor_config['params']
            processor_class = data_processors.get(processor_name)

            if not processor_class:
                return jsonify({'response': f"Unsupported processor {processor_name}"}), 400

            processor = processor_class()
            processed_data = processor.process(processed_data)

        # Step 3: Store the processed data into the vector DB
        db_to_use = channel_config['db_configs'][0]
        db_class = db_classes.get(db_to_use['type'])
        if not db_class:
            return jsonify({'response': "Unsupported database type"})

        if db_to_use['type'] == "vector":
            db = db_class(db_to_use['path'], embeddings_model=db_to_use['embeddings_model'])
        else:
            db = db_class(db_to_use['path'])
        
        db.store(processed_data)

        return jsonify({'response': "Data ingested successfully"}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
