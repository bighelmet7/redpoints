from flask import Flask

def create_app(config_obj='mlteam.config.DevelopmentConfig'):
    """
    Returns an app Flask object configurated with the given config_obj.
    """
    app = Flask(__name__)
    app.config.from_object(config_obj)

    from v1.blueprint import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from mlteam.extensions import redis_client
    redis_client.init_app(app)

    from flask_cors import CORS
    CORS(app)

    return app
