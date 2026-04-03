from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from .routes import jobs, feedback, settings
    app.register_blueprint(jobs.bp)
    app.register_blueprint(feedback.bp)
    app.register_blueprint(settings.bp)

    with app.app_context():
        from . import models
        db.create_all()

    return app
