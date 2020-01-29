from .app import create_app

APP = create_app()

#gunicorn twitoff:APP -t 1200
#FLASK_APP=twitoff:APP flask run
