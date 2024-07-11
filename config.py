
import os

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
    PROMPT_TEMPLATE = os.getenv('PROMPT_TEMPLATE')
    LLM_MODEL = os.getenv('LLM_MODEL')
    EMBED_MODEL = os.getenv('EMBED_MODEL')