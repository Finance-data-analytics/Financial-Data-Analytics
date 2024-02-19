from threading import Thread

from flask import Flask
from flask_session import Session  # Import the Session class
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from data_retrieval import generate_plotting_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:8889/neoma_venturedb'
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
app.config['SESSION_TYPE'] = 'filesystem'  # Specify the session type to filesystem
app.config['SESSION_FILE_DIR'] = './project/session_file'  # Make sure to provide the path to store sessapp.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_register_page"
login_manager.login_message_category = "info"

# Configure cache
app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)

# Initialize the session interface with the app
Session(app)

def background_data_fetch():
    with app.app_context():
        plotting_data = generate_plotting_data()
        cache.set("plotting_data", plotting_data)


bg_thread = Thread(target=background_data_fetch)
bg_thread.start()


from project import routes
