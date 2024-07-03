from openai import OpenAI
import certifi
import os

client = OpenAI(
    base_url="https://api.gptsapi.net/v1",
    api_key="sk-eGpa07ec077a782096252d4e83597b30db776cbb1e5kbYhb"
)

# os.environ['SSL_CERT_FILE'] = 'C:\\Users\\wante\\Desktop\\GenAI\\chatbot_project\\chatbot_project\\cacert.pem'


completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are system assistant."},
    {"role": "user", "content": "Hi"}
  ],
  timeout=60
)

print(completion.choices[0].message)