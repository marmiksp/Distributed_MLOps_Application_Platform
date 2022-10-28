from flask import Flask,json,request
import pymongo, pytz
import json, requests
from pytz import timezone
from threading import Thread
from datetime import datetime,date,timedelta
import math
import heapq
from flask_cors import CORS, cross_origin



app = Flask(__name__)

"""
Database for fault tolerance
"""
myclient=pymongo.MongoClient("mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority")
mydb=myclient["Hackathon"]
mycollection=mydb["Scheduler_db"]
sess = requests.Session()

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
#     "node_manager": {
#         "base_url": "http://localhost:" + str(NODE_PORT),
#         "uri": {
#             "get_schedule_app": "/get_schedule_app"
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
#     "app_manager": {
#         "base_url": "http://localhost:" + str(APP_PORT),
#         "uri": {
#             "get_all_models_sensos": "/get_models_sensors",
#             "get_all_apps": "/get_all_applications",
#             "get_sensor_by_app_id": "/get_sensor_by_app_id",
#             "deploy_app": "/deploy"
#         }
#     },
# }

def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

constants = read_json("constants.json")
servers=read_json("servers.json")


Scheduler_queue=[]
Termination_queue=[]

@app.route('/sendInfo',methods=['POST'])
def getUserInput():
    #print("72")
    response=request.get_json()
    print(response)
    #print("74")
    """
    response={
        app_inst_id: str
        start_time: str
        end_time: float
        stand_alone: bool
    }
    1)add response to Scheduler_db
    2)take start time, end time, request id
      andadd to first priority queue 
    """
    #1
    mycollection.insert_one(response)
    #print("88")
   
    #2
    heapq.heappush(Scheduler_queue,(response["start_time"],response["end_time"],response["app_inst_id"],response["stand_alone"]))
    #print("92")
    result={
        "status":"true",
        "message":"Application Scheduled..."
    }
    
    return json.dumps(result)



def deployerApp(appInfo):
    deployer_obj={}
    deployer_obj["app_inst_id"]=appInfo[2]
    deployer_obj["stand_alone"]=appInfo[3]
    deployer_obj["end_status"]=0

    # print("72...sending to node manager to deploy")
    response=sess.post(servers[constants["VM_MAPPING"]["NODE"]]+constants["PORT"]["NODE_PORT"]+constants["ENDPOINTS"]["NODE_MANAGER"]["get_schedule_app"],json=deployer_obj).json()

    """
    1)response status = true
        1.1)calculate the end time
        1.2)take end time, req id, stand_alone,
            and add to the second priority queue
    2)delete entry from Scheduler_db since the app is now scheduled and deployed
    2)update a new field in mongo doc= kill_time
    """

    #1
    print(response["message"]) #"App is deployed or not"
    if response["status"]=="true":
        #1.1
        duration=float(appInfo[1])
        days_num=duration/int(24)
        rem=duration%24
        hours=math.floor(rem)
        min=math.floor((rem-hours)*60)
        date_time = datetime.strptime(appInfo[0] + ":00", '%Y-%m-%d %H:%M:%S')
        end_date=date_time + timedelta(days=days_num)
        end_time=str(end_date)+" "+str(hours)+":"+str(min)
        end_time = end_time.rsplit(':',2)[0]
        #this end_time is  String
        #1.2
        heapq.heappush(Termination_queue,(end_time,appInfo[2]))
    
    #2
    # mycollection.delete_one({"app_inst_id": appInfo[2]})
    mycollection.update_one({"app_inst_id":appInfo[2]},{"$set":{"kill_time":end_time}})
   


def scheduling_function():
    
    while(True):
        if Scheduler_queue:
            while str(datetime.now(pytz.timezone('Asia/Kolkata'))).rsplit(':',1)[0]<Scheduler_queue[0][0]:
                pass
            appInfo = heapq.heappop(Scheduler_queue)
            #appInfo is a tuple that has 4 fields : start_time, end_time, app_inst_id, stand_alone
            deployerApp(appInfo)

def termination_function():
    
    while(True):
        if Termination_queue:
            # print("118 --- ",Termination_queue[0][0])
            while str(datetime.now(pytz.timezone('Asia/Kolkata'))).rsplit(':',1)[0]<Termination_queue[0][0]:
                pass
            # print("121 termination function ",str(datetime.now()).rsplit(':',1)[0])
            appInstId = heapq.heappop(Termination_queue)[1]
            deployer_obj={}
            deployer_obj["app_inst_id"]=appInstId
            deployer_obj["end_status"]=1
             
            response=sess.post(servers[constants["VM_MAPPING"]["NODE"]]+constants["PORT"]["NODE_PORT"]+constants["ENDPOINTS"]["NODE_MANAGER"]["get_schedule_app"],json=deployer_obj).json()
            #response=sess.post(endpoint['node_manager']['base_url'] + endpoint['node_manager']['uri']['get_schedule_app'],json=deployer_obj).json()
            mycollection.delete_one({"app_inst_id": appInstId})
            print(response["message"]) #application killed or not

if __name__=="__main__":
    """
    1)thread1 = to continuously check if start time of any app in scheduling queue has come
    2)thread2 = to check continuously if end time of any deployed app has been reached
    """
    thread1=Thread(target=scheduling_function)
    thread2=Thread(target=termination_function)
    thread1.start()
    thread2.start()

    app.run(host='0.0.0.0', port=constants["PORT"]["SCHEDULER_PORT"])

    thread1.join()
    thread2.join()
