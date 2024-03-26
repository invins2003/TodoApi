from flask import Flask
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request,session
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

app.secret_key = "secretkey"

app.config['MONGO_URI'] = "mongodb://localhost:27017/USERS"

mongo = PyMongo(app)



# sign up
@app.route('/add',methods=['POST'])   
def add_user():
     _json = request.json
     _name =  _json['name']
     _email = _json['email']
     _password = _json['pwd']
     
     if _name and _email and _password and request.method == 'POST':
         _hashed_password = generate_password_hash(_password)
         id = mongo.db.user.insert_one({'name':_name,'email':_email,'pwd':_hashed_password})
         response  = jsonify("user add succesfully")
         response.status_code = 200
         return response
     else :
         return not_found()

# sign in
@app.route('/signin', methods=['POST'])
def sign_in():
    _json = request.json
    _email = _json['email']
    _password = _json['pwd']

    user = mongo.db.user.find_one({'email': _email})

    if user and check_password_hash(user['pwd'], _password):
        session['email'] = _email
        response = jsonify("Login successful!")
        response.status_code = 200
        return response
    else:
        response = jsonify("Invalid email or password")
        response.status_code = 401
        return response 
    
# Sign out
@app.route('/signout', methods=['GET'])
def sign_out():
    if 'email' in session:
        session.pop('email', None)
        return jsonify("YOU ARE LOGGED OUT") 
    else:
        return jsonify("You are not logged in."), 401
     
     
#All users
@app.route('/users',methods=['GET'])   
def users():
    users = mongo.db.user.find()
    response= dumps(users)   
    return response

# display a apecific user
@app.route('/user/<id>')  
def user(id):
    user=mongo.db.user.find_one({'_id':ObjectId(id)}) 
    response = dumps(user)
    return response

# delete user from one collection and sending it to another collection
@app.route("/delete/<id>", methods=["DELETE"])
def delete_user(id):
    user = mongo.db.user.find_one({"_id": ObjectId(id)})
    if user:
        mongo.db.deleted_user.insert_one(user)
        mongo.db.user.delete_one({"_id": ObjectId(id)})
        response = jsonify("User deleted successfully!")
        response.status_code = 200
    else:
        response=not_found(404)  
    return response

# update profile
@app.route('/update/<id>',methods=['PUT'])
def update_user(id):
    _id = id
    _json = request.json
    _name =  _json['name']
    _email = _json['email']
    _password = _json['pwd']
    if _name and _email and _password and _id and request.method=='PUT':
        user = mongo.db.user.find_one({"_id": ObjectId(id)})
        mongo.db.old_user_data.insert_one(user)
        _hashed_password = generate_password_hash(_password)
        mongo.db.user.update_one({'id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},{'$set':{'name':_name,'email':_email,'pwd':_hashed_password}})
        response = jsonify("user updated successfully")
        return response    
        
# error handler
@app.errorhandler(404)
def not_found(error=None):
         message = {
             'status':404,
             'message':'Not Found ' + request.url
         }
         response = jsonify(message)
         response.status_code = 404
         return response
     
     
if __name__ == "__main__":
    app.run(debug=True)     