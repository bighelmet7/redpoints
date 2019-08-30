from flask import Flask, g
from redis import Redis

def create_app(config_obj='mlteam.config.DevelopmentConfig'):
    """
    Returns an app Flask object configurated with the given config_obj.
    """
    app = Flask(__name__)
    app.config.from_object(config_obj)

    from flask_cors import CORS
    CORS(app)

    return app
