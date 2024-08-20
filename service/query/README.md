# Support Genius Query Service

This is an GenAI-based backend service, which provides rest api to chat with LLM.

## Setup

1. Clone the repository.
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Add your config to `app/config/channel_config.yaml`
4. Add your prompt templates to `app/prompt_templates`.
5. Run the application:
    ```
    python run.py
    ```

## Usage

HTTP POST call `http://localhost:5001/chat/<channel>` with below request body to chat with LLM:
```
{
    "prompt": "<your query>",
    "send_to_reviewer": false
}
```
