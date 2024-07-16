from flask import request, jsonify
import logging
import json
from app.video_processing import handle_video_url

def register_routes(app, socketio, settings):

    @app.route('/')
    def root():
        return "Premiere is alive", 200
    
    @app.route('/get-version', methods=['GET'])
    def get_version():
        return jsonify(version='2.1.2') 


    @app.route('/settings', methods=['POST'])
    def update_settings():
        try:
            new_settings = request.get_json()
            with open(settings['SETTINGS_FILE'], 'w') as f:
                json.dump(new_settings, f, indent=4)
            # Update the in-memory settings as well
            settings.update(new_settings)
            return jsonify(success=True), 200
        except KeyError as e:
            logging.error(f"KeyError: {e}")
            return jsonify(success=False, error=f"Missing key: {e}"), 400
        except Exception as e:
            logging.error(f"Exception: {e}")
            return jsonify(success=False, error=str(e)), 500

    @app.route('/handle-video-url', methods=['POST'])
    def handle_video_url_route():
        return handle_video_url(request, settings, socketio)
