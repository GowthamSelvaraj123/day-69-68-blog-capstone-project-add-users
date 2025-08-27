from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_ckeditor import CKEditor
import hashlib

db = SQLAlchemy()
login_manager = LoginManager()
ckeditor = CKEditor()

from app.routes.main import main
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    db_path = os.path.join(app.instance_path, 'posts.db')
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    ckeditor.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def hashlib_md5(text):
        return hashlib.md5(text.strip().lower().encode('utf-8')).hexdigest()

    app.jinja_env.filters['hashlib_md5'] = hashlib_md5

    with app.app_context():
        from .models import User, BlogPost, Comment
        db.create_all()
    app.register_blueprint(main)
    return app

