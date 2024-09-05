from app import main
from flask import Flask
import os

app = Flask(__name__)
app.register_blueprint(main)

print("Current working directory:", os.getcwd())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
