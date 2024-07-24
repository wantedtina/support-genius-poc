from tools.prompt_loader import PromptLoader
from config import Config


def test_loader_prompt():
    prompt = PromptLoader(Config.PROMPT_PATH).load_prompt("prompt_test", "extract_query")
    print(prompt)

