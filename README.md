# ChatGPT Support Assistant Bot

This is an enhanced ChatGPT bot built with Flask and OpenAI's API. The bot is designed as a support assistant for specific technical issues.

## Setup

1. Clone the repository.
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Add your prompt template to `/prompt`
3. Set the OpenAI API key, base url, prompt template as an environment variable in .env (you may need to create one if not existed in workspace):
    ```
    OPENAI_API_KEY=xxx
    OPENAI_BASE_URL=https://xxx
    PROMPT_TEMPLATE=prompt/prompt_template.json
    LLM_MODEL=gpt-4
    EMBED_MODEL=text-embedding-ada-002
    PROMPT_PATH=prompt/
    ```
4. Add your knowledge base to `/data`.
5. Run the application:
    ```
    python run.py
    ```

## Usage

Open your browser and navigate to `http://127.0.0.1:5000` to interact with the support assistant bot.
