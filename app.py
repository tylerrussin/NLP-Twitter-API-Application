from os import getenv
from flask import Flask, render_template

DATABASE_URL = getenv('DATABASE_URL')

app = Flask(__name__)



@app.route('/')
def index():
    test = ['user1', 'user2', 'user3']
    test2 = ['some information one', 'some info 2']
    return render_template('base.html', title='Home', users=test, comparisons=test2)