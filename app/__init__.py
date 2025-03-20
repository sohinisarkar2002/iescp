from flask import Flask
from .routes import main


def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.register_blueprint(main)
    app.config['SECRET_KEY'] = 'sdasndcsn&ifedhiosn@#wo4530hsjwh'

    return app
