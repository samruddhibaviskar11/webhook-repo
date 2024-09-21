from flask import request, jsonify
from datetime import datetime
from . import webhook_bp
from ..extensions import mongo
import logging

logging.basicConfig(level=logging.INFO)

@webhook_bp.route('/webhook/', methods=['POST'])  # Correct route
def receive_webhook():
    logging.info('Webhook received: %s', request.json)
    
    data = request.json
    if 'action' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    author = data['sender']['login']
    timestamp = datetime.utcnow().strftime('%d %B %Y - %I:%M %p UTC')

    if data['action'] == 'push':
        to_branch = data['ref'].split('/')[-1]
        message = f'{author} pushed to {to_branch} on {timestamp}'
        
    elif data['action'] == 'pull_request':
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        message = f'{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}'
        
    else:
        return jsonify({'error': 'Unsupported action'}), 400

    # Check for duplicates
    existing_event = mongo.db.events.find_one({'message': message})
    if existing_event:
        return jsonify({'status': 'ignored', 'message': message}), 200  # Ignore duplicates

    # Store message in MongoDB
    try:
        mongo.db.events.insert_one({
            'message': message,
            'timestamp': datetime.utcnow()
        })
    except Exception as e:
        logging.error('Error storing event: %s', str(e))
        return jsonify({'error': 'Failed to store event'}), 500

    return jsonify({'status': 'success', 'message': message}), 200
