from flask import Flask, jsonify, request
from datetime import datetime
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb://localhost:27017/USERS"

mongo = PyMongo(app)

@app.route('/sendMessages/<id>', methods=['POST'])
def send_messages(id):
    _json = request.json
    user = mongo.db.user.find_one({"_id": ObjectId(id)})
    if user:
        _name = user.get('name')
        _message = _json.get('message')
        _ticket = bool(_json.get('ticket', False))
        _status = bool(_json.get('status', True))
        if _message:
            _time = datetime.now().isoformat()
            message_data = {
                'name': _name,
                'message': _message,
                'TS': _time,
                'ticket': _ticket,
                'status': _status
            }
            mongo.db.message_Data.insert_one(message_data)
            response = get_messages()
            return jsonify(response), 200
        else:
            return jsonify({'error': 'Message is required'}), 400
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/getMessages', methods=['GET'])
def get_messages():
    messages = mongo.db.message_Data.find()
    response = dumps(messages)
    return response, 200
@app.route('/updateMessage/<message_id>', methods=['PUT'])
def update_message(message_id):
    _json = request.json
    _ticket = bool(_json.get('ticket'))
    _status = bool(_json.get('status'))

    mongo.db.message_Data.update_one({'_id': ObjectId(message_id)}, {'$set': {'ticket': _ticket, 'status': _status}})
    updated_message = mongo.db.message_Data.find_one({'_id': ObjectId(message_id)})
    if updated_message:
        # Convert ObjectId to string before returning the response
        updated_message['_id'] = str(updated_message['_id'])
        response = {
            'message': 'Message updated successfully',
            'updated_message': updated_message
        }
        return jsonify(response), 200
    else:
        return jsonify({'error': 'Message not found'}), 404

if __name__ == "__main__":
    app.run(debug=True)
