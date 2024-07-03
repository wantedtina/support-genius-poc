from flask import Blueprint, request, jsonify, render_template
from openai import OpenAI
import os
from .knowledge_base import KnowledgeBase

main = Blueprint('main', __name__)
knowledge_base = KnowledgeBase('data')

# Ensure the OpenAI API key is set
client = OpenAI(
    base_url="your-base-url",
    api_key="your-api-key"
)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '')

    kb_response = knowledge_base.search(prompt)
    if kb_response:
        return jsonify({'response': kb_response})

    # get knowledge base
    knowledge_text = knowledge_base.get_knowledge_text()

    complete_prompt = (
            f"# CONTEXT #\n"
            f"This is a support chat application called Support Genius.\n"
            f"# OBJECTIVE #\n"
            f"Provide accurate and helpful information based on the user's question using the knowledge base.\n"
            f"# STYLE #\n"
            f"Professional and friendly.\n"
            f"# TONE #\n"
            f"Professional and friendly.\n"
            f"# AUDIENCE #\n"
            f"Users seeking support for various issues.\n"
            f"# RESPONSE #\n"
            f"Support Genius Knowledge Base:\n{knowledge_text}\n\n"
            f"User's question: {prompt}\n\n"
            f"# GUARDRAILS #\n"
            f"If the user's question is not found in the knowledge base, respond with 'Sorry, it is out of my scope'. "
            f"Do not provide answers that are not found in the knowledge base."
        )
    

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a support assistant for Automation Anywhere and PowerShell."},
            {"role": "user", "content": complete_prompt}
        ],
        timeout=60  # Increase timeout to 60 seconds
    )
    return jsonify({'response': response.choices[0].message.content})
