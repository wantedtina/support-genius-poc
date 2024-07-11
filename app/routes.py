from flask import Blueprint, request, jsonify, render_template
from openai import OpenAI
import os
from .knowledge_indexer import KnowledgeIndexer
from config import Config
import json

main = Blueprint('main', __name__)
knowledge_indexer = KnowledgeIndexer('data')

# Load prompt template from JSON file
with open(Config.PROMPT_TEMPLATE, 'r') as file:
    prompt_template = json.load(file)['template']

# Ensure the OpenAI API key is set
client = OpenAI(
    base_url=Config.OPENAI_BASE_URL,
    api_key=Config.OPENAI_API_KEY
)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '')

    # get knowledge base
    relevant_docs = knowledge_indexer.search(prompt)
    knowledge_text = "\n".join(relevant_docs)

    complete_prompt = prompt_template.format(knowledge=knowledge_text, question=prompt)

    response = client.chat.completions.create(
        model=Config.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a support assistant for Automation Anywhere."},
            {"role": "user", "content": complete_prompt}
        ],
        timeout=60  # Increase timeout to 60 seconds
    )
    return jsonify({'response': response.choices[0].message.content})
