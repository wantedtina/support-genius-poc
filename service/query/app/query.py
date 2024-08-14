from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import uuid
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from .db.vector_db import VectorDB
from .utils.config_loader import load_config
from .prompt_template.template_loader import TemplateLoader
from .query_processor.query_construction_vector import QueryConstructorVector
from .query_processor.query_translator import QueryTranslator
from .query_processor.routing import Routing
from .data_retrieval import reranking
from .generation import generation
from openai import OpenAI

main = Blueprint('main', __name__)

# Ensure the OpenAI API key is set
client = OpenAI(
)

# 加载配置
config = load_config('config/channel_config.yaml')

vector_dbs = {
    "vector": VectorDB,
    # 可以添加其他类型的数据库
}

template_loader = TemplateLoader(config['template_path'])
prompt_processor_vector = QueryConstructorVector()

@main.route('/chat/<channel>', methods=['POST'])
def main(channel):
    channel_config = config['channels'].get(channel)

    data = request.json
    prompt = data.get('prompt', '')

    # 加载提示模板用于Query, Translator, Routing, Constructor
    prompt_template = TemplateLoader.load_template(channel_config['prompt_template'])
    prompt_template_translator = TemplateLoader.load_template(channel_config['prompt_template_translator'])
    prompt_template_routing = TemplateLoader.load_template(channel_config['prompt_template_routing'])
    prompt_template_constructor = TemplateLoader.load_template(channel_config['prompt_template_constructor'])

    # 处理prompt
    QueryTranslator
    Routing

    db_class = vector_dbs[channel_config['db_type']]
    db = db_class(channel_config['db_path'])

    # 搜索数据
    relevant_docs = db.search(prompt)

    knowledge_text = "\n".join([doc['content'] for doc in relevant_docs])    

    complete_prompt = QueryConstructorVector.construct(prompt_template, knowledge_text, prompt)

    response = client.chat.completions.create(
        model=config['openai']['model'],
        messages=[
            {"role": "system", "content": "You are a support assistant for Automation Anywhere."},
            {"role": "user", "content": complete_prompt}
        ],
        timeout=60  # Increase timeout to 60 seconds
    )

    api_response = response.choices[0].message.content

    reranking
    generation
