from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    return app, socketio
