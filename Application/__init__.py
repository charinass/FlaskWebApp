from flask import Flask
from .models import db


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + 'Db/db.sqlite'

    db.init_app(app)

    # to create db
    # db.create_all()

    return app


app = create_app()

from .App import views