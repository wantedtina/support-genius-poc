import os
from pathlib import Path
import yaml


class PromptLoader:
    def __init__(self, root_dir=None):
        self.root_dir = root_dir
        if self.root_dir is None:
            self.root_dir = Path(__file__).resolve().parent.parent.joinpath("prompt")

    def load_prompt(self, prompt_file, prompt_key) -> str:
        prompt_file = prompt_file + ".ymal"
        with open(os.path.join(self.root_dir, prompt_file), "r") as f:
            prompt = yaml.load(f, Loader=yaml.FullLoader)
            return prompt[prompt_key]
