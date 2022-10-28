from flask import Flask, request
import requests
import os
import sys
import json
from threading import Thread
from azure.storage.fileshare import ShareFileClient
from generate_docker_file import generate_dockerfile
import file_storage
import psutil
from zipfile import ZipFile
from kafka.consumer import KafkaConsumer
from kafka.producer import KafkaProducer
import pymongo
import shutil
from bson import ObjectId

session = requests.Session()
app = Flask(__name__)

def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

constants = read_json("constants.json")
servers = read_json("servers.json")

IP_ADDR = constants["KAFKA_HOST_ADDR"]
VM1_PORT = 9650
CONNECTION_STR = "https://hackathonfilestorage.file.core.windows.net/DefaultEndpointsProtocol=https;AccountName=hackathonfilestorage;AccountKey=gdZHKPvMvlkDnpMcxMxu2diC/bRqvjptH7qJlbx5VI/95L/p6H932ZOTZwg5kuWbyUJ6Y8TCrh3nqIlyG+YD2g==;EndpointSuffix=core.windows.net"
vmip1 = "20.219.100.230"

myclient=pymongo.MongoClient("mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority")
mydb=myclient["Hackathon"]
nodedb=mydb["Node_db"]
# appdb = mydb["app_inst_db"]
appdb = mydb["AppInstance"]

node_info = nodedb.find_one({"ip":vmip1})
node_id = str(node_info["_id"])

# client = SSHClient()
port_dict = dict()
ports = {
    8010 : "False",
    8011 : "False",
    8012 : "False",
    8013 : "False",
    8014 : "False",
    8015 : "False",
    8016 : "False",
    8017 : "False",
    8018 : "False",
    8019 : "False",
    8020 : "False"
}

def unzip_file(file_name,source_folder):
    '''
    unzips the file to folder of same name
    '''
    with ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(source_folder)

def send_cpu_util():
    ram_percent = psutil.virtual_memory().percent
    return str(ram_percent)

def run_application(app_inst_id):
    
    curr_port = None
    for curr_port in ports.keys():
        if ports[curr_port] == "False":
            key = curr_port
            break
    if key == None:
        return {"status" : "false", "message" : "No Port Available"}
    
    port_dict[app_inst_id] = key

    temp = nodedb.update_one({ "_id": ObjectId(node_id)},
                { "$push": { 'list_of_app_inst': app_inst_id}}
                )

    for x in appdb.find():
        if str(x["_id"]) == app_inst_id:
            appdb.update_one({"_id" : ObjectId(app_inst_id)}, {"$set" : {"node_id" : node_id}})
            app_path = x["docker_image"]
            break

    file_storage.download_file(app_inst_id + ".zip", app_inst_id + ".zip")
    unzip_file(app_inst_id + ".zip",os.getcwd()+"/"+app_inst_id)
    os.remove(app_inst_id + ".zip")

    generate_dockerfile(curr_port, os.getcwd() + "/" + app_inst_id)

    os.system(f"zip -r {app_inst_id}.zip {app_inst_id}")
    os.system(f"sshpass -p 'Abc@azureuser' scp -o StrictHostKeyChecking=no {app_inst_id}.zip azureuser@20.219.100.230:/home/azureuser/code/ias-hackathon")
    os.system(f"sshpass -p Abc@azureuser ssh azureuser@20.219.100.230 'cd /home/azureuser/code/ias-hackathon;unzip {app_inst_id}.zip;cd {app_inst_id};sudo docker build -t {app_inst_id}:latest .;sudo docker run --net=host -it -d -p {curr_port}:{curr_port} {app_inst_id}'")

    print("app running at port {}".format(curr_port))
    
    ports[curr_port] = "True"
    status = {
        "status":"true",
        "message":"Deployed!"
    }
    print(curr_port)
    return status
        

def stop_application(app_inst_id):
    if port_dict[app_inst_id] == None:
        print("port dictionary empty!")
        status = {
            "status":"true",
            "message":"Port Dictionary empty for given app instance id!"
        }
        return status

    kill_port = port_dict[app_inst_id]

    for x in appdb.find():
        if str(x["_id"]) == app_inst_id:
            node_id = x["node_id"]
            print(x)
            print(x["node_id"])
            appdb.delete_one(x)
            print("Deletion done in appdb")
            break
    
    temp = nodedb.update_one({ "_id": ObjectId(node_id) },
                        { "$pull": { 'list_of_app_inst': app_inst_id } }
                    )
            

    print("kill_time")
    os.system(f"sshpass -p Abc@azureuser ssh azureuser@20.219.100.230 'sudo docker stop $(sudo docker ps -q --filter ancestor={app_inst_id});sudo docker image remove -f {app_inst_id}'")

    ports[kill_port] = "False"

    del port_dict[app_inst_id]
    shutil.rmtree(app_inst_id)
    status = {
        "status":"true",
        "message":"Process Killed!"
    }
    return status

def read_topic():
    consumer = KafkaConsumer(
            "Node_topic",
            bootstrap_servers = [IP_ADDR],
            auto_offset_reset = 'earliest',
            # consumer_timeout_ms = 2000
            group_id=vmip1
        )

    producer=KafkaProducer(
            bootstrap_servers = [IP_ADDR],
            value_serializer = lambda x: json.dumps(x).encode('utf-8')
        )

    for msg in consumer:
        command = json.loads(msg.value)
        commands = command.split()

        if commands[0] == "get_cpu_util":
            ram_percent = send_cpu_util()
            data = vmip1 + " " + str(ram_percent)
            print(data)
            producer.send(topic = "LB_topic", value = data)
        elif commands[0] == "run" and commands[1] == vmip1:
            status = run_application(commands[2])
        elif command[0] == "stop" and commands[1] == vmip1:
            status = stop_application(commands[2])
        else:
            continue

if __name__=="__main__":

    thread1=Thread(target=read_topic)
    thread1.start()
    
    app.run(host='0.0.0.0', port=constants["PORT"]["VM1_PORT"])

    thread1.join()
