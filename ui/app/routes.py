from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('user_chat.html')

@main.route('/reviewer')
def reviewer():
    return render_template('reviewer_chat.html')
