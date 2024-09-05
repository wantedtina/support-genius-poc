from flask import Blueprint, request, jsonify, Response
from openai import OpenAI
import ollama
from .utils.config_loader import load_config
from .prompt_templates.template_loader import TemplateLoader
from .query_processor import QueryTranslator, LogicalRouting, SemanticRouting, QueryConstructor
from .db.es_db import EsDB
from .db.graph_db import GraphDB
from .db.sql_db import SqlDB
from .db.vector_db import VectorDB
from .data_retriever import Reranking
from time import sleep

main = Blueprint('main', __name__)

# Setup a logger to store logs
log_messages = []

def log_message(message):
    log_messages.append(message)
    print(message)  # You can also log to console

# Load Config
config = load_config('app/config/channel_config.yaml')

# Load Query Processor
query_processors = {
    "query_translator": QueryTranslator,
    "query_logical_routing": LogicalRouting,
    "query_semantic_routing": SemanticRouting,
    "query_constructor": QueryConstructor
}

# Load DB
db_classes = {
    "vector": VectorDB,
    "sql": SqlDB,
    "es": EsDB,
    "graph": GraphDB
}

# Load Data Retriever
data_retriever = {
    "reranking": Reranking,
}

# Load prompt template from yaml file
template_loader  = TemplateLoader(config['template_path'])

# Set up LLM Client
def create_llm_client(llm_config):
    if llm_config['type'] == "openai":
        return OpenAI(
            base_url=llm_config['base_url'],
            api_key=llm_config['api_key']
        )
    elif llm_config['type'] == "ollama":
        return ollama.Client(
            # base_url=llm_config['base_url'],
            # api_key=llm_config['api_key']
        )
    else:
        raise ValueError(f"Unsupported LLM type: {llm_config['type']}")

@main.route('/chat/<channel>', methods=['POST'])
def chat(channel):
    global log_messages
    log_messages = []  # Clear previous logs
    log_message("Starting to process your request...")
    sleep(1)
    channel_config = config['channels'].get(channel)
    if not channel_config:
        return jsonify({'response': "Invalid channel"})
    
    log_message("Channel selected...")
    sleep(1)

    data = request.json
    prompt = data.get('prompt', '')
    send_to_reviewer = data.get('send_to_reviewer', False)

    # Instance LLM Client
    llm_type = channel_config['llm']['type']
    llm_client = create_llm_client(channel_config['llm'])

    # Load prompt templates for each steps
    prompt_template =  template_loader.load_template(channel_config['prompt_template'])

    # Initialize the list of queries
    queries = [prompt]  # Start with the original query

     # Define the required running order
    processor_order = ["query_translator", "query_logical_routing", "query_semantic_routing", "query_constructor"]

    # Implement query processors
    # TODO: refactor as per your requirement
    db_to_use = None
    for processor_name in processor_order:
        processor_config = next((p for p in channel_config['query_processor'] if p['name'] == processor_name), None)
        if processor_config:
            processor_params = processor_config['params']
            processor_class = query_processors[processor_name]
            if not processor_class:
                return jsonify({'response': f"Unsupported processor {processor_name}"})

            processor_llm_client = create_llm_client(processor_params['llm'])
            processor = processor_class(template_loader=template_loader, llm=processor_llm_client)

            # TODO: consider parameter and return value of routing might be difference from query translation & construction
            if processor_name == "query_translator":
                # Expect multiple queries as output
                queries = processor.process(queries[0])  # Replace the initial query with the generated queries
            elif processor_name == "query_logical_routing":
                # Process the first query in case it's expected to be single (or adjust logic to handle multiple queries)
                # TODO: implement logical routing
                db_to_use = processor.process(queries[0], channel_config['db_configs'])
            else:
                # Process each query generated by the QueryTranslator
                processed_queries = []
                for query in queries:
                    result = processor.process(query)
                    if isinstance(result, list):
                        processed_queries.extend(result)
                    else:
                        processed_queries.append(result)
                queries = processed_queries

    # At this point, queries should contain the final processed queries
    # Connect to DB
    if db_to_use:
        db_class = db_classes.get(db_to_use['type'])
        if not db_class:
            return jsonify({'response': "Unsupported database type"})

        if db_to_use['type'] == "vector":
            db = db_class(db_to_use['path'], embeddings_model=db_to_use['embeddings_model'])
        else:
            db = db_class(db_to_use['path'])

    # Search in DB
    relevant_docs = db.search(prompt)
    knowledge_text = "\n".join([doc.page_content for doc in relevant_docs])
    
    print("knowledge_text: " + knowledge_text)

    complete_prompt = prompt_template.format(knowledge=knowledge_text, question=prompt)

    if llm_type == "openai":
        response = llm_client.chat.completions.create(
            model=channel_config['llm']['model'],
            messages=[
                {"role": "system", "content": channel_config['system_prompt']},
                {"role": "user", "content": complete_prompt}
            ],
            timeout=60  # Increase timeout to 60 seconds
        )
        api_response = response.choices[0].message.content ##openai

    if llm_type == "ollama":
        response = llm_client.chat(
            model=channel_config['llm']['model'],
            messages=[
                {"role": "system", "content": channel_config['system_prompt']},
                {"role": "user", "content": complete_prompt}
            ]
        )
        api_response = response['message']['content'] ## Llama

    # return jsonify({'response': response['message']['content']})   

    log_message("Response ready!")
    sleep(1)

    if send_to_reviewer:
        add_pending_review(api_response, prompt)
        return jsonify({'response': api_response})
    else:
        send_to_user(api_response, prompt)
        return jsonify({'response': api_response})

@main.route('/chat_logs/<channel>', methods=['GET'])
def chat_logs(channel):
    def generate_logs():
        for message in log_messages:
            yield f"data: {message}\n\n"
            sleep(1)  # Simulate real-time streaming

    return Response(generate_logs(), content_type='text/event-stream')

@main.route('/pending_reviews')
def pending_reviews():
    return jsonify({'reviews': get_pending_reviews()})


@main.route('/review', methods=['POST'])
def review():
    data = request.json
    action = data.get('action', '')
    response = data.get('response', '')
    user_prompt = data.get('user_prompt', '')

    if action == 'approve':
        send_to_user(response, user_prompt)
        return jsonify({'response': response})
    elif action == 'reject':
        send_to_user("Sorry, it is out of my scope", user_prompt)
        return jsonify({'response': "Sorry, it is out of my scope"})
    elif action == 'pending':
        add_pending_review(response, user_prompt)
        return jsonify({'status': 'pending'})


@main.route('/user_responses')
def user_responses():
    return jsonify({'responses': get_user_responses()})


pending_reviews = []
user_responses = []


def get_pending_reviews():
    return pending_reviews


def add_pending_review(response, user_prompt):
    pending_reviews.append({'response': response, 'user_prompt': user_prompt})


def get_user_responses():
    global user_responses
    responses = user_responses
    user_responses = []
    return responses


def send_to_user(response, user_prompt):
    user_responses.append({'response': response, 'user_prompt': user_prompt})
    print(f"Response to user ({user_prompt}): {response}")
