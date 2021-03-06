from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time
from bson import json_util

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')

# database
db = client['DSMarkets']
# collections
users = db['Users']
products = db['Products']

# Flask App
app = Flask(__name__)

users_sessions = {}

# function for creating uid
def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  

# function for checking if uid is valid
def is_session_valid(user_uuid):
    return user_uuid in users_sessions

# create simple user
@app.route('/createSimpleUser', methods=['POST'])
def create_simple_user():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data or not "e-mail" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    # if user not in database already
    if users.find({"e-mail":data["e-mail"]}).count() == 0 :
	# update category for simple user
        category = {'category':'simple user'}
        data.update(category)
        users.insert_one(data) # add user
        return Response("User "+data['name']+" was added.\n", mimetype='application/json', status=200) 
    else: # if user already in database 
        return Response("A user with the given email already exists\n", mimetype='application/json', status=400) 

# login
@app.route('/login', methods=['POST'])
def login():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # if email or password is not given
    if not "e-mail" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    # if email, password found in database
    if users.find_one({"e-mail":data["e-mail"], "password":data["password"]}):
	# call function create session, return uuid
        user_uuid = create_session(data["e-mail"])
        return Response('Userid for user ' + data['e-mail']+ ' : '+ user_uuid+"\n", mimetype='application/json',status=200) 
    else:
        return Response("Wrong email or password.\n",mimetype='application/json', status=400) 

# add product - admin
@app.route('/addProduct', methods=['POST'])
def add_product():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data or not "name" in data or not "price" in data or not "category" in data or not "stock" in data or not "description" in data:
        return Response("Id, Name, price, description, category and stock must be inserted.\n")
    # if product not in database already
    if products.find({"id":data["id"]}).count() == 0 :
        products.insert_one(data) # add product
        return Response('Product '+data['name']+' was added to database.\n', mimetype='application/json', status=200) 
    else:
        return Response('Product with id '+data['id']+' already exists in database.\n', mimetype='application/json', status=200)
        

# delete product - admin
@app.route('/deleteProduct', methods=['DELETE'])
def delete_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # if no id given
    if not "id" in data:
        return Response("No product specified by id!\n",status=500,mimetype="application/json")
    product = products.find_one({'id':data["id"]})
    # if product exists
    if product != None:
        # delete product
        products.delete_one(product)
        return Response ("Product with id "+product["id"] + " was deleted.\n", status=200, mimetype='application/json')
    else: # if no student product found
        return Response("No product found with id " + data["id"]+"\n")


# update product - admin
@app.route('/updateProduct', methods=['UPDATE'])
def update_product():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # if no id given
    if not "id" in data:
        return Response("No product specified by id!\n",status=500,mimetype="application/json")
    # find product
    product = products.find_one({'id':data["id"]})
    # if product exists
    if product != None:
        # update product by name
        if "name" in data:
            products.update_one({'id':data["id"]},{'$set': {'name':data["name"]}})
        # update product by price
        if "price" in data:
            products.update_one({'id':data["id"]},{'$set': {'price':data["price"]}})
        # update product by description
        if "description" in data:
            products.update_one({'id':data["id"]},{'$set': {'description':data["description"]}})
        # update product by stock
        if "stock" in data:
            products.update_one({'id':data["id"]},{'$set': {'stock':data["stock"]}})
        return Response("Product "+product["id"]+" updated successfully.\n", status=200, mimetype='application/json')
    else: # if no product found
            return Response("No product with id:" + data["id"]+"\n")
         

# find product
@app.route('/getProduct', methods=['GET'])
def get_product():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data and not "category" and not "id":
        return Response("Information incomplete", status=500, mimetype="application/json")
    # Get uuid from header type authorization
    uuid = request.headers.get('Authorization')
    # Check if uuid is valid
    verify = is_session_valid(uuid)
    if verify:
	# Find product(s) by name
        if "name" in data:
            productsList = products.find({'name':data["name"]})
            productsArray = []
            # store data in dictionary
            for product in productsList:
		# print name, descr, price, category, id
                product = {'name': product["name"], 'description': product["description"], 'price': product["price"],  'category':product["category"], 'id':product["id"]}
                productsArray.append(product)
                # sort array by name
                productsArray = sorted(productsArray, key = lambda i: i['name'])
	    # If product(s) found, print
            if productsArray != []:
                return Response(json.dumps(productsArray,indent=4)+"\n", status=200, mimetype='application/json')
            else: # if no product found
                return Response("No product(s) found named '"+data["name"]+"'.\n")
	# Find product(s) by category
        elif "category" in data:
            productsList = products.find({'category':data["category"]})
            productsArray = []
	    # store data in dictionary
            for product in productsList:
		 # print name, descr, price, category, id  
                 product = {'name': product["name"], 'description': product["description"], 'price': product["price"],  'category':product["category"], 'id':product["id"]}
                 productsArray.append(product)
                 # sort array by price
                 productsArray = sorted(productsArray, key = lambda i: i['price'])
            # If product(s) found, print
            if productsArray != []:
                return Response(json.dumps(productsArray,indent=4)+"\n", status=200, mimetype='application/json')
            else: # if no product found
                return Response("No product(s) found in category '"+data["category"]+"'.\n")
	# Find product by id
        elif "id" in data:
            product = products.find_one({'id':data["id"]})
            if product != None:
		# print name, descr, price, category, id
                product = {'name': product["name"], 'description': product["description"], 'price': product["price"],  'category':product["category"], 'id':product["id"]}
                return Response(json.dumps(product,indent=4)+"\n", status=200, mimetype='application/json')
            else: # if no product found
                return Response("No product found with id '"+data["id"]+"'.\n")
    else: # If uuid was not valid
        return Response("User can't be verified.\n", status=401)


# add product to cart
@app.route('/addToCart', methods=['PATCH'])
def add_to_cart():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # check if no data missing
    if not "e-mail" in data or not "id" in data or not "quantity":
        return Response("Complete your email, product id and quantity\n",status=500,mimetype="application/json")
    # Get uuid from header type authorization
    uuid = request.headers.get('Authorization')
    # Check if uuid is valid
    verify = is_session_valid(uuid)
    if verify:
        # find product by id
        product = products.find_one({'id':data["id"]})
        if product != None:
            # check if enough products in stock
            if int(data["quantity"]) <= int(product["stock"]):
                total_cost = 0;
                quantity = 0;
                price = 0;
                # find user
                user = users.find_one({'e-mail':data["e-mail"]})
                # if user has a cart, update cart
                if "cart" in user:
                    user["cart"].update({product["id"]: data["quantity"]})
                    users.update_one({'e-mail':data["e-mail"]},{'$set': {'cart':user["cart"]}})
                    for product_id in user["cart"]:
                        # find cart product in db
                        item = products.find_one({'id':product_id})
                        # find product's price
                        price = (float)(item["price"])
                        # get quantity from user data
                        quantity = user["cart"].get(product_id)
                        # calculate total cost
                        total_cost = total_cost + price * float(quantity)
                    return Response("Product added succesfully to cart!\nYour cart:\n"+json.dumps(user["cart"],indent=4)+"\nTotal cost: "+str(total_cost)+"???\n", status=200, mimetype='application/json')
                # if no cart exists, create
                else:
                    users.update_one({'e-mail':data["e-mail"]},{'$set': {'cart':{product["id"]: data["quantity"]}}})
                    # find cart product in db
                    item = products.find_one({'id':product["id"]})
                    # find product's price
                    price = (float)(item["price"])
                    # get quantity from user data
                    quantity = data["quantity"]
                    # calculate total cost
                    total_cost = total_cost + price * float(quantity)
                    return Response("Product added succesfully to cart!\nYour cart:\n"+json.dumps({product["id"]: data["quantity"]},indent=4)+"\nTotal cost: "+str(total_cost)+"???\n", status=200, mimetype='application/json')
            else: # if product out of stock
                return Response("Product not available, out of stock.\n")
        else: # if no product found
            return Response("No product found with id '"+data["id"]+"'.\n")
    else: # If uuid was not valid
        return Response("User can't be verified.\n", status=401)

# get cart
@app.route('/getCart', methods=['GET'])
def get_cart():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "e-mail" in data:
        return Response("No user selected!\n", status=500, mimetype="application/json")
    # Get uuid from header type authorization
    uuid = request.headers.get('Authorization')
    # Check if uuid is valid
    verify = is_session_valid(uuid)
    if verify:
        total_cost = 0;
        quantity = 0;
        price = 0;
        # find user
        user = users.find_one({'e-mail':data["e-mail"]})
        for product_id in user["cart"]:
            # find cart product in db
            item = products.find_one({'id':product_id})
            # find product's price
            price = (float)(item["price"])
            # get quantity from user data
            quantity = user["cart"].get(product_id)
            # calculate total cost
            total_cost = total_cost + price * float(quantity)
        return Response("Your cart:\n"+json.dumps(user["cart"],indent=4)+"\nTotal cost: "+str(total_cost)+"???\n", status=200, mimetype='application/json')	
    else: # If uuid was not valid
        return Response("User can't be verified.\n", status=401)

# delete product from cart
@app.route('/deleteFromCart', methods=['PATCH'])
def delete_from_cart():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # check if no data missing
    if not "e-mail" in data or not "id" in data:
        return Response("Complete your email and product you want to delete!\n",status=500,mimetype="application/json")
    # Get uuid from header type authorization
    uuid = request.headers.get('Authorization')
    # Check if uuid is valid
    verify = is_session_valid(uuid)
    if verify:
        # find user by email
        user = users.find_one({'e-mail':data["e-mail"]})
        # find product in cart
        if data["id"] in user["cart"]:
            total_cost = 0;
            quantity = 0;
            price = 0;
            # updated cart, delete product with id
            new_cart = user["cart"].pop(data["id"])
            # update db
            users.update_one({'e-mail':data["e-mail"]},{'$set': {'cart':new_cart}})
            # calculate total cost for cart
            for product_id in user["cart"]:
                # find cart product in db
                item = products.find_one({'id':product_id})
                # find product's price
                price = (float)(item["price"])
                # get quantity from user data
                quantity = user["cart"].get(product_id)
                # calculate total cost
                total_cost = total_cost + price * float(quantity)
            return Response("Product deleted succesfully!\nYour cart:\n"+json.dumps(user["cart"],indent=4)+"\nTotal cost: "+str(total_cost)+"???\n", status=200, mimetype='application/json')
        else: # if no product found
            return Response("No product found with id '"+data["id"]+"' in your cart.\n")
    else: # If uuid was not valid
        return Response("User can't be verified.\n", status=401)

# buy products
@app.route('/buyProducts', methods=['PATCH'])
def buy_products():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # check if no data missing
    if not "e-mail" in data or not "card-number" in data:
        return Response("Complete your email and card number!\n", status=500, mimetype="application/json")
    # Get uuid from header type authorization
    uuid = request.headers.get('Authorization')
    # Check if uuid is valid
    verify = is_session_valid(uuid)
    if verify:
        # find user by email
        user = users.find_one({'e-mail':data["e-mail"]})
        # check if cart is not empty
        if user["cart"] != {}:
            # check if card number contains 16 digits
            if len(data["card-number"]) == 16:
                order = [] # store orders
                # if history already exists
                if "orderHistory" in user:
                    order.append(user["orderHistory"])  # store old orders
                    order.append({'order':user["cart"]}) # add new order
                else: # if no history exists
                    order = {'order':user["cart"]} # store new order
                # add order(s) to history
                users.update_one({'e-mail':data["e-mail"]},{'$set': {'orderHistory':order}})
                # delete cart
                new_cart = {}
                users.update({'e-mail':data["e-mail"]},{'$set': {'cart':new_cart}})
                receipt = 'product id.....quantity.......price\n' # receipt format
                total_cost = 0;
                quantity = 0;
                price = 0;
                for item in user["cart"]: # for each item in cart
                    product = products.find_one({'id':item})
                    price = (float)(product["price"]) # find product's price
                    quantity = user["cart"].get(item) # get quantity
                    cost = price * float(quantity) # cost for each item
                    total_cost = total_cost + cost # calculate total cost 
                    # receipt
                    receipt = receipt + "    "+item+ "............."+user["cart"].get(item)+"............"+str(cost)+"???\n"
                # return receipt and total cost
                return Response("Your receipt:\n"+receipt+"---------------------------------------\n    Total Cost: "+str(total_cost)+"???\n", status=200, mimetype='application/json')
            else: # if card number not 16 digits
                return Response("Invalid card number. Card number must be 16 digits.\n")
        else: # if cart empty
            return Response("No products in cart!\n")
    else: # If uuid was not valid
        return Response("User can't be verified.\n", status=401)

# get order history
@app.route('/getHistory', methods=['GET'])
def get_history():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # check if no data missing
    if not "e-mail" in data:
        return Response("Complete your email!\n", status=500, mimetype="application/json")
    # Get uuid from header type authorization
    uuid = request.headers.get('Authorization')
    # Check if uuid is valid
    verify = is_session_valid(uuid)
    if verify:
        # find user by email
        user = users.find_one({'e-mail':data["e-mail"]})
        # check if user has an order history, return
        if "orderHistory" in user:
            return Response ("Your order history:\n"+json.dumps(user["orderHistory"],indent=4)+"\n", status=200, mimetype='application/json')
        else: # if no history exists
            return Response("No order history founs!\n")
    else: # If uuid was not valid
        return Response("User can't be verified.\n", status=401) # error message
        
# delete user
@app.route('/deleteUser', methods=['DELETE'])
def delete_user():
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # if no id given
    if not "e-mail" in data:
        return Response("No e-mail specified!\n",status=500,mimetype="application/json")
    # Get uuid from header type authorization
    uuid = request.headers.get('Authorization')
    # Check if uuid is valid
    verify = is_session_valid(uuid)
    if verify:
        user = users.find_one({'e-mail':data["e-mail"]})
        # if user exists, delete
        if user != None:
            users.delete_one(user)
            return Response (user["name"] + " was deleted.\n", status=200, mimetype='application/json')
        else:
            return Response("No user found with email " + data["e-mail"]+"\n")
    else: # If uuid was not valid
        return Response("User can't be verified.\n", status=401)

'''#Helping methods
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
        return Response(data['name']+" was added as an admin", mimetype='application/json', status=200)
    else: # id user already in database 
        return Response("A user with the given email already exists", mimetype='application/json', status=400)
'''

# ???????????????? flask service ???? debug mode, ???????? port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)[0]
