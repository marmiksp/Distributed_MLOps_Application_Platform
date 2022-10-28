from flask import Flask, request
import requests
import pymongo
import sys,json

session = requests.Session()
app = Flask(__name__)
myclient=pymongo.MongoClient("mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority")
mydb=myclient["Hackathon"]
mycollection=mydb["Node_db"]

def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

constants = read_json("constants.json")

# SENSOR_PORT = 9100
# MODEL_PORT = 9200
# LOAD_PORT = 9300
# APP_PORT = 9400
# DEPLOYER_PORT = 9900
# NODE_PORT = 9500
# SCH_PORT = 9600


# endpoint = {
#     "sensor_manager": {
#         "base_url": "http://localhost:"+str(SENSOR_PORT), 
#         "uri": {
#             "sensorinfo": "/sensorinfo",
#             "getsensordata": "/getsensordata"
#         }
#     },
#     "app_manager": {
#         "base_url": "http://localhost:" + str(APP_PORT),
#         "uri": {
#             "get_all_models_sensos": "/get_models_sensors",
#             "get_all_apps": "/get_all_applications",
#             "get_sensor_by_app_id": "/get_sensor_by_app_id",
#             "deploy_app": "/deploy"
#         }
#     },
#     "load_balancer": {
#         "base_url": "http://localhost:" + str(LOAD_PORT),
#         "uri": {
#             "get_node_id": "/get_node_id"
#         }
#     },
#     "deployer": {
#         "base_url": "http://localhost:" + str(DEPLOYER_PORT),
#         "uri": {
#             "send_to_deployer": "/send_to_deployer",
#         }
#     },
# }

def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

constants = read_json("constants.json")


@app.route("/get_node_id", methods=["POST"])
def get_node_id():
    req = request.get_json()
    """
    req={
        'stand_alone': bool
    }
    we will ignore stand_alone for now
    and do load balancing on basis of num of apps running
    """

    min_load=1e9
    resultant_node=""
    for x in mycollection.find():
        if len(x['list_of_app_inst'])<min_load:
            min_load=len(x['list_of_app_inst'])
            resultant_node=str(x['_id'])
    reply={
        'node_id':resultant_node,
        'message':"Node Assigned.."
    }
    return reply


if __name__=="__main__":
    app.run(host='0.0.0.0', port=constants["PORT"]["LOAD_PORT"], debug=True)
