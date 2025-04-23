import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


db = SQLAlchemy()



def create_app():
    db_path = os.path.abspath("testdb.sqlite3")
    app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/")
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{db_path}'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "bhfdiejfhgjfdfbvjv"

    db.init_app(app)

    

    login_manager = LoginManager()
    login_manager.init_app(app)

    bcrypt = Bcrypt()
    
    from models import User,Subject,Scores,Questions,Quiz
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    with app.app_context():
        db.create_all()

    

        from routes import register_routes
        register_routes(app,db,bcrypt)

        migrate = Migrate(app, db)

    
    return app




