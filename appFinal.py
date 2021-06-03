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

# Create admin
@app.route('/createAdmin', methods=['POST'])
def create_admin():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data or not "e-mail" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    # if admin not in database
    if users.find({"e-mail":data["e-mail"]}).count() == 0 :
	# update
        category = {'category':'admin'}
        data.update(category)
        users.insert_one(data) # add admin
        return Response(data['name']+" was added as an admin", mimetype='application/json', status=200) # return success message
    else: # id user already in database 
        return Response("A user with the given email already exists", mimetype='application/json', status=400) # return error message


# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)[0]

