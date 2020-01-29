import uuid
from decouple import config
from dotenv import load_dotenv
from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .twitter import add_user

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    DB.init_app(app)

    @app.route('/index')
    def index():
        rand_name = str(uuid.uuid4())
        rand_u = User(name=rand_name)
        DB.session.add(rand_u)
        DB.session.commit()
        return 'Index Page'

    @app.route('/')
    def root():

        return render_template('base.html', title='users', users = User.query.all())

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method ==  'POST':
                add_user(name)
                message = "User {} successfuly added!".format(name)
            #import pdb; pdb.set_trace()
            tweets = User.query.filter(User.name==name).one().tweets
        except Exception as e:
            message = 'Error adding {}: {}'.format(name, e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets, message=message)
    return app
