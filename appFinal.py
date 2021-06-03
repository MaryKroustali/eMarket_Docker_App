from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time
from bson import json_util

# Connect local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['DSMarkets']

# Choose collections
users = db['Users']
products = db['Products']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    return user_uuid in users_sessions


# Get users
@app.route('/getallusers', methods=['GET'])
def get_all_users():
    iterable = users.find({})
    output = []
    for user in iterable:
        user['_id'] = None
        output.append(user)
    return jsonify(output)

# Get products
@app.route('/getallproducts', methods=['GET'])
def get_all_products():
    iterable = products.find({})
    output = []
    for product in iterable:
        product['_id'] = None
        output.append(product)
    return jsonify(output) # original format
    # return json.dumps(json.loads(json_util.dumps(output))) # for ids


# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)[0]

