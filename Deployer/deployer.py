from flask import Flask, request
import requests
from paramiko import SSHClient
import pymongo
from flask_cors import CORS, cross_origin
from bson import ObjectId
import zipfile
import json
from kafka.producer import KafkaProducer


session = requests.Session()
app = Flask(__name__)
cors = CORS(app)

def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

constants = read_json("constants.json")
servers = read_json("servers.json")

IP_ADDR = constants["KAFKA_HOST_ADDR"]
CONNECTION_STR = "https://hackathonfilestorage.file.core.windows.net/DefaultEndpointsProtocol=https;AccountName=hackathonfilestorage;AccountKey=gdZHKPvMvlkDnpMcxMxu2diC/bRqvjptH7qJlbx5VI/95L/p6H932ZOTZwg5kuWbyUJ6Y8TCrh3nqIlyG+YD2g==;EndpointSuffix=core.windows.net"

session = requests.Session()
app = Flask(__name__)
client = SSHClient()
myclient=pymongo.MongoClient("mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority")
mydb=myclient["Hackathon"]
nodedb=mydb["Node_db"]
appdb = mydb["AppInstance"]

# base_url = "http://localhost:8080"

# ports = 9751
# port_dict = dict()
# ports = {
#     2000 : "False",
#     2001 : "False",
#     2002 : "False",
#     2003 : "False",
#     2004 : "False",
#     2005 : "False"
# }

producer=KafkaProducer(
            bootstrap_servers = [IP_ADDR],
            value_serializer = lambda x: json.dumps(x).encode('utf-8')
        )

def unzip_file(file_name,source_folder):
    '''
    unzips the file to folder of same name
    '''
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(source_folder)

@app.route("/")
@cross_origin()
def hello():
    return ""

@app.route("/send_to_deployer", methods=["POST"])
def send_to_deployer():
    print("Starting Deployment")
    req = request.get_json()
    
    node_id = req["node_id"]
    app_inst_id = req["app_inst_id"]
    print("app instance : ", app_inst_id)

    """
    1) if node_id==""
        this means that the app is already running and it has to be killed
        1.1)goto appInsDB and fetch node_id
        1.2)delete that row from appInst db
        1.3)corresponding to the node_id, get the pid from dict and kill the process
        1.4)delete the appInstId from NodeDb list of inst of that node

    2) otherwise run the app at the given node

    """

    #1
    if node_id == "":
        app_info = appdb.find_one({"_id": ObjectId(app_inst_id)})
        nodeid = app_info["node_id"]
        print("Going to kill the app on node id:", str(node_id))
        node_info = nodedb.find_one({"_id":ObjectId(nodeid)})
        nodeip = node_info["ip"]

        command = "stop " + nodeip + " " + app_inst_id

        producer.send(topic = "Node_topic", value = command)

        status = {
            "status":"true",
            "message":"Process Killed!"
        }
        
    else:
        print("Gonna launch app on this node: ", str(node_id))
        node_info = nodedb.find_one({"_id":ObjectId(node_id)})
        nodeip = node_info["ip"]

        command = "run " + nodeip + " " + app_inst_id

        producer.send(topic = "Node_topic", value = command)
        
        status = {
            "status":"true",
            "message":"Deployed!"
        }

    return status

if __name__=="__main__":
    app.run(host="0.0.0.0", port=constants["PORT"]["DEPLOYER_PORT"], debug=True) 