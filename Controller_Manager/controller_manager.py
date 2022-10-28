from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import json, os
import kafka_util 


app = Flask(__name__)
cors = CORS(app)

app.config['SECRET_KEY'] = "dub_nation"

DB_SERVER = "mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority"
client = MongoClient(DB_SERVER)
HACKATHON_DB = client['Hackathon']

ctrl_type_db = HACKATHON_DB['ControllerTypeDB']
ctrl_instance_db = HACKATHON_DB['ControllerInstanceDB']

def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

constants = read_json("constants.json")
servers = read_json("servers.json")


def init_controller():
    ctrl_instance_list = ctrl_instance_db.find()
    if ctrl_instance_list:
        for ctrl_instance in ctrl_instance_list:
            os.system(f"""sshpass -p Yash@1998 ssh yash@localhost 
                'gnome-terminal python3 controller_instance.py {ctrl_instance["_id"]}'
            """)


@app.route("/")
def hello_controller():
    return render_template("controller_home.html",
        home = servers[constants["VM_MAPPING"]["APP"]] + constants["PORT"]["APP_PORT"] + constants["ENDPOINTS"]["APP_MANAGER"]["home"],
        add_ctrl_type_api = servers[constants["VM_MAPPING"]["CONTROLLER"]] + constants["PORT"]["CONTROLLER_PORT"] + constants["ENDPOINTS"]["CONTROLLER_MANAGER"]["add_controller_type"],
        add_ctrl_instance_api = servers[constants["VM_MAPPING"]["CONTROLLER"]] + constants["PORT"]["CONTROLLER_PORT"] + constants["ENDPOINTS"]["CONTROLLER_MANAGER"]["add_controller_instance"],
        sensor_url = servers[constants["VM_MAPPING"]["SENSOR"]] + constants["PORT"]["SENSOR_PORT"] + constants["ENDPOINTS"]["SENSOR_MANAGER"]["admin"],
    )


@app.route("/add_controller_type", methods=["POST"])
def add_controller_type():
    ctrl_name = request.form.get("ctrl_name")
    ctrl_op = request.form.get("ctrl_op")

    ctrl_doc = ctrl_type_db.find_one({"ctrl_name": ctrl_name})
    if ctrl_doc:
        return jsonify({'message': 'Controller type already exists', 'status_code': 500}), 500
    
    ctrl_type_db.insert_one({"ctrl_name": ctrl_name, "ctrl_op": ctrl_op})
    return jsonify({'message': 'Controller type added successfully', 'status_code': 200}), 200


@app.route("/get_controller_list", methods=["GET"])
def get_controller_list():
    ctrl_list = ctrl_type_db.find()
    ctrl_list_json = []
    for ctrl in ctrl_list:
        ctrl_list_json.append(ctrl["ctrl_name"])
    return jsonify(ctrl_list_json), 200


@app.route("/add_controller_instance", methods=["POST"])
def add_controller_instance():
    ctrl_type = request.form.get("ctrl_type")
    location = request.form.get("location")
    ctrl_ip = request.form.get("ctrl_ip")
    ctrl_port = request.form.get("ctrl_port")

    try:
        id = ctrl_instance_db.insert_one({"ctrl_type": ctrl_type, "location": location, "ctrl_ip": ctrl_ip, "ctrl_port": ctrl_port})
        kafka_util.create_topic(id.inserted_id)
        return jsonify({'message': 'Controller instance added successfully', 'status_code': 200}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Unable to add controller instance', 'status_code': 500}), 500


@app.route("/get_controller_instance_list", methods=["POST"])
def get_controller_instance_list():
    try:
        ctrl_list = ctrl_instance_db.find()
        ctrl_list_json = []
        for ctrl in ctrl_list:
            ctrl_list_json.append(ctrl)
        return jsonify(ctrl_list_json), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Unable to get controller instance list', 'status_code': 500}), 500


@app.route("/get_controller_instance_details_by_location", methods=["POST"])
def get_controller_instance_details_by_location():
    """
    This Fn return the controller instance details by location
    @param location: location of the controller instance
    @return: controller instance details
        {'status_code': 200 , response: ['ctrl_type': <type_value>, 'ctrl_insance_list': <list>]}
    """
    req = request.get_json()
    ctrl_instance_doc = ctrl_instance_db.find({"location": req["location"]})
    print(ctrl_instance_doc)
    if ctrl_instance_doc:
        resp = {}
        for ctrl_instance in ctrl_instance_doc:
            if ctrl_instance["location"] == req["location"]:
            
                if ctrl_instance["ctrl_type"] not in resp:
                    resp[ctrl_instance["ctrl_type"]] = []
            
                resp[ctrl_instance["ctrl_type"]].append({
                    "ctrl_ip": ctrl_instance["ctrl_ip"],
                    "ctrl_port": ctrl_instance["ctrl_port"],
                    "ctrl_instance_id": str(ctrl_instance["_id"])
                })

            response = []
            for ctrl_type in resp:
                response.append({
                    "ctrl_type": ctrl_type,
                    "ctrl_instance_list": resp[ctrl_type]
                })
        return jsonify({'status_code': 200, 'response': response}), 200
    else:
        return jsonify({'message': 'Unable to get controller instance details', 'status_code': 500}), 500


if __name__ == "__main__":
    # init_controller()
    app.run(host='0.0.0.0', port=constants["PORT"]["CONTROLLER_PORT"], debug=True)
