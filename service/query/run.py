from app import main
from flask import Flask
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire application
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
