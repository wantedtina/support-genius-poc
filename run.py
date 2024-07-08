
from app import create_app
import openai
from config import Config

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
