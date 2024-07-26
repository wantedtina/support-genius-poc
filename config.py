import os


class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
    LLM_MODEL = os.getenv('LLM_MODEL')
    EMBED_MODEL = os.getenv('EMBED_MODEL')
    PROMPT_PATH = os.getenv('PROMPT_PATH')
