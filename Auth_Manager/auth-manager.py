from flask import Flask, jsonify, make_response, redirect, request, url_for
from pymongo import MongoClient
import datetime
from flask_cors import CORS, cross_origin
import requests
import hashlib
import json
import jwt


app = Flask(__name__)
cors = CORS(app)
req_sess = requests.Session()

app.config['SECRET_KEY'] = "dub_nation"

DB_SERVER = "mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority"
client = MongoClient(DB_SERVER) #client -> cluster -> collection
HACKATHON_DB = client['Hackathon']

user_db = HACKATHON_DB['UserDB']


def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

constants = read_json("constants.json")
servers = read_json("servers.json")

@app.route("/register", methods=["POST"])
@cross_origin()
def register():
	new_user = request.get_json()
	new_user["password"] = hashlib.sha256(new_user['password'].encode("utf-8")).hexdigest()

	doc = user_db.find_one({"username": new_user["username"]})
	if not doc:
		user_db.insert_one(new_user)
		return jsonify({'message': 'User created successfully, please proceed with login', 'status_code': 200}), 200
	else:
		return jsonify({'message': 'Username already exists', 'status_code': 500}), 500


@app.route("/login", methods=["POST"])
@cross_origin()
def login():
    login_details = request.get_json()
    print(login_details)
    user_from_db = user_db.find_one({'username': login_details['username']})
    print(user_from_db)
    
    if user_from_db:
        encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        role = user_from_db['role']
        
        if role != login_details['role']:
            return jsonify({'message': 'Please check your role', 'status_code': 500}), 500

        if encrpted_password == user_from_db['password']:
            print("user verified to be in database with correct password")
            access_token = jwt.encode(
                {'username': user_from_db['username'], 'role': user_from_db['role']}, 
                app.config['SECRET_KEY'], 
                algorithm='HS256'
            )

            if not isinstance(access_token, str):
                access_token = access_token.decode("utf-8")

            print(access_token)
            resp = jsonify({'access_token': access_token, 'status_code': 200}), 200
            return resp
        else:
            return jsonify({'message': 'Please check your username or password', 'status_code': 401}), 401
    else:
        return jsonify({'message': 'Username does not exist', 'status_code': 401}), 401


@app.route("/logout")
def logout():
    print(request.args['jwt'])
    token = request.args['jwt']
    data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
    return redirect(servers[constants["VM_MAPPING"]["APP"]] + constants["PORT"]["APP_PORT"] + constants["ENDPOINTS"]["APP_MANAGER"]["home"])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=constants["PORT"]["AUTH_PORT"], debug=True)
