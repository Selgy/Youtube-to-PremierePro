import os
import time
import logging
import threading
import platform
import sys
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from app.routes import register_routes
from app.utils import load_settings, monitor_premiere_and_shutdown

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

should_shutdown = False

def run_server():
    settings = load_settings()
    logging.info('Settings loaded: %s', settings)
    register_routes(app, socketio, settings)

    server_thread = threading.Thread(target=lambda: socketio.run(app, host='localhost', port=3001, allow_unsafe_werkzeug=True))
    server_thread.start()

    premiere_monitor_thread = threading.Thread(target=monitor_premiere_and_shutdown_wrapper)
    premiere_monitor_thread.start()

    while not should_shutdown:
        time.sleep(1)

    logging.info("Shutting down the application.")
    os._exit(0)

def monitor_premiere_and_shutdown_wrapper():
    global should_shutdown
    monitor_premiere_and_shutdown()
    should_shutdown = True

if __name__ == "__main__":
    run_server()
