import uuid
from decouple import config
from dotenv import load_dotenv
from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .twitter import add_user, update_all_users, add_default_users
from .predict import predict_user

load_dotenv()

recent_list = []

# Initializing the Flask App
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
        DB.create_all()

        return render_template('base.html', title='Home', users=User.query.all(), comparisons=recent_list)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method ==  'POST':
                add_user(name)
                message = "User {} successfuly added!".format(name)

            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = 'Error adding {}: {}'.format(name, e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets, message=message)

    @app.route('/compare', methods=['POST'])
    def compare(message=''):

        user1 = request.values['user1']
        user2 = request.values['user2']
        tweet_text = request.values['tweet_text']

        if user1 == user2:
            message = 'Cannot compare a user to themselves'
        else:

            prediction = predict_user(user1, user2, tweet_text)

            message = '"{}" is more likely to be said by {} than {}'.format(
                request.values['tweet_text'], user1 if prediction else user2,
                user2 if prediction else user1)
            
            recent_list.append(message)

        return render_template('prediction.html', title='Prediction', message=message)

    # Resets the heroku database
    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='Reset database!')

    # Uploades twitter data to database
    @app.route('/update')
    def update():
        update_all_users()
        return render_template('base.html', users=User.query.all(), title='All Tweets updated!')

    # Default users to be uploaded on start
    @app.route('/add_default')
    def add_default():
        add_default_users()
        return render_template('base.html', users=User.query.all(), title='Reset database!')

    return app
