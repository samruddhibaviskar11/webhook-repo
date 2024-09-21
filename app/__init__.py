from flask import Flask, render_template, jsonify
from .extensions import mongo
from .webhook import webhook_bp

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/github_webhook_db'

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    app.register_blueprint(webhook_bp)

    # Define routes inside the create_app function
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/api/events', methods=['GET'])
    def get_events():
        events = mongo.db.events.find().sort('timestamp', -1)  # Sort by latest
        return jsonify([{'message': event['message']} for event in events])

    return app
