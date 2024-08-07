import os.path

from flask import Blueprint, request, jsonify, render_template
from openai import OpenAI
from .knowledge_indexer import KnowledgeIndexer
from .data_processor import get_data_processor
from .vector_db import get_vector_db
from config import Config
import json
import ollama
from tools.prompt_loader import PromptLoader
from config import Config
import glob
from datetime import date
from tools.prompt_loader import PromptLoader
import yaml

main = Blueprint('main', __name__)

# 加载配置
# def load_config(path):
#     with open(path, 'r') as file:
#         return yaml.load(file, Loader=yaml.FullLoader)

# config = load_config('config.yaml')

knowledge_indexer_confluence = KnowledgeIndexer('data', 'faiss_index/confluence', 'pdf')
knowledge_indexer_sn = KnowledgeIndexer('data', 'faiss_index/serviceNow', 'json')

# Load prompt template from yaml file
prompt_template_confluence = PromptLoader(Config.PROMPT_PATH).load_prompt("prompt_confluence", "extract_query")
prompt_template_sn = PromptLoader(Config.PROMPT_PATH).load_prompt("prompt_sn", "extract_query")

# Ensure the OpenAI API key is set
client = OpenAI(
    base_url=Config.OPENAI_BASE_URL,
    api_key=Config.OPENAI_API_KEY
)


@main.route('/')
def index():
    return render_template('user_chat.html')


@main.route('/reviewer')
def reviewer():
    return render_template('reviewer_chat.html')


@main.route('/chat/<channel>', methods=['POST'])
def chat(channel):
    data = request.json
    prompt = data.get('prompt', '')
    send_to_reviewer = data.get('send_to_reviewer', False)

    # channel_config = next((ch for ch in config['channels'] if ch['name'] == channel), None)
    # if not channel_config:
    #     return jsonify({'response': "Invalid channel"})

    # processor = get_data_processor(channel_config['data_processor'])
    # vector_db = get_vector_db(channel_config['vector_db'], channel_config['db_config'])

    # 假设get_data_from_source方法从数据源获取数据
    # data = get_data_from_source(channel_config['data_source'])
    # processed_data = processor.process(data)
    # vector_db.store(processed_data)

    # relevant_docs = vector_db.search(prompt)
    # prompt_template = PromptLoader(Config.PROMPT_PATH).load_prompt(channel_config['prompt'], "extract_query")

    if channel == 'confluence':
        relevant_docs = knowledge_indexer_confluence.search(prompt)
        prompt_template = prompt_template_confluence
        knowledge_text = "\n".join(relevant_docs)
    elif channel == 'sn':
        relevant_docs = knowledge_indexer_sn.search(prompt)
        prompt_template = prompt_template_sn
        knowledge_text = ''
        for doc in relevant_docs:
            knowledge_text += doc.page_content + "\n"
        print("knowledge_text: " + knowledge_text)
    else:
        return jsonify({'response': "Invalid channel"})
    # knowledge_text = "\n".join(relevant_docs)

    complete_prompt = prompt_template.format(knowledge=knowledge_text, question=prompt)

    response = client.chat.completions.create(
        model=Config.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a support assistant for Automation Anywhere."},
            {"role": "user", "content": complete_prompt}
        ],
        timeout=60  # Increase timeout to 60 seconds
    )

    # response = ollama.chat(
    #     model='llama3',
    #     messages=[
    #         {"role": "system", "content": "You are a support assistant for Automation Anywhere."},
    #         {"role": "user", "content": complete_prompt}
    #     ]
    # )
    # return jsonify({'response': response['message']['content']})

    api_response = response.choices[0].message.content
    if send_to_reviewer:
        add_pending_review(api_response, prompt)
        return jsonify({'response': api_response})
    else:
        send_to_user(api_response, prompt)
        return jsonify({'response': api_response})


@main.route('/pending_reviews')
def pending_reviews():
    # 返回待审核的响应
    return jsonify({'reviews': get_pending_reviews()})


@main.route('/review', methods=['POST'])
def review():
    data = request.json
    action = data.get('action', '')
    response = data.get('response', '')
    user_prompt = data.get('user_prompt', '')

    if action == 'approve':
        # 将批准的响应发送回用户
        send_to_user(response, user_prompt)
        return jsonify({'response': response})
    elif action == 'reject':
        # 将拒绝的响应发送回用户
        send_to_user("Sorry, it is out of my scope", user_prompt)
        return jsonify({'response': "Sorry, it is out of my scope"})
    elif action == 'pending':
        # 将待审核的响应存储到全局变量或数据库
        add_pending_review(response, user_prompt)
        return jsonify({'status': 'pending'})


@main.route('/user_responses')
def user_responses():
    # 返回所有用户的响应
    return jsonify({'responses': get_user_responses()})


# 全局变量或数据库管理待审核响应
pending_reviews = []
user_responses = []


def get_pending_reviews():
    return pending_reviews


def add_pending_review(response, user_prompt):
    pending_reviews.append({'response': response, 'user_prompt': user_prompt})


def get_user_responses():
    global user_responses
    responses = user_responses
    user_responses = []  # 清空用户响应列表
    return responses


def send_to_user(response, user_prompt):
    user_responses.append({'response': response, 'user_prompt': user_prompt})
    print(f"Response to user ({user_prompt}): {response}")
