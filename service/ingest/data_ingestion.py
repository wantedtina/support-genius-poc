from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import uuid
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from .data_loader import JsonLoader, HtmlLoader, PdfLoader
from .data_processor import JsonProcessor, HtmlProcessor, PdfProcessor
from .db.vector_db import VectorDB
from .utils.config_loader import load_config
from .prompt_template.template_loader import TemplateLoader

# 加载配置
config = load_config('config/channel_config.yaml')

# 动态加载组件
data_loaders = {
    "json": JsonLoader,
    "html": HtmlLoader,
    "pdf": PdfLoader
}

data_processors = {
    "json": JsonProcessor,
    "html": HtmlProcessor,
    "pdf": PdfProcessor
}

vector_dbs = {
    "vector": VectorDB,
    # 可以添加其他类型的数据库
}

template_loader = TemplateLoader(config['template_path'])

def main(channel):
    channel_config = config['channels'].get(channel)
     # 加载数据
    loader_class = data_loaders[channel_config['data_loader']]
    loader = loader_class(channel_config['data_source'])
    raw_data = loader.load_data()

    # 加载提示模板用于Indexing, retrieval, generation
    prompt_template_index = TemplateLoader.load_template(channel_config['prompt_template_index'])
    prompt_template_retrieval = TemplateLoader.load_template(channel_config['prompt_template_retrieval'])

    # 处理数据
    processor_class = data_processors[channel_config['data_processor']]
    processor = processor_class()
    processed_data = processor.process(raw_data)

    # 存储数据
    db_class = vector_dbs[channel_config['db_type']]
    db = db_class(channel_config['db_path'])
    db.store(processed_data)
