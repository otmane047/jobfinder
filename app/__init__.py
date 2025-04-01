from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Configuration des sessions côté serveur
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '../flask_sessions'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 heure

Session(app)
socketio = SocketIO(app, cors_allowed_origins="*")

from app.views.auth_views import auth_bp
from app.views.chat_views import chat_bp
from app.views.job_views import job_bp
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(job_bp)

