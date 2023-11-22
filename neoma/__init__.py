from threading import Thread

from flask import Flask, session
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from data_retrieval import generate_plotting_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/neoma_venturedb'
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_register_page"
login_manager.login_message_category = "info"

# Global variable to store plotting data
app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)


def background_data_fetch():
    with app.app_context():
        plotting_data = generate_plotting_data()
        cache.set("plotting_data", plotting_data)

bg_thread = Thread(target=background_data_fetch)
bg_thread.start()

from neoma import routes
