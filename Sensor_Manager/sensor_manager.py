from flask import Flask,render_template,request,redirect
import random
import json
import time
import threading
import os
import pymongo
import jwt
from flask_cors import CORS, cross_origin

# from init_sensor import *
from kafka_fun import *
CONST=""
with open("constants.json","r") as f:
    CONST = json.load(f)

with open("servers.json","r") as f:
    SERV = json.load(f)


############################################## List of APIs #######################################################

# @app.route("/")
# @app.route("/is_sensor_manager_alive")
# @app.route('/appdev_insert_type/<string:sensor_type>/<string:output_type>')
# @app.route('/list_of_sensortypes')
# @app.route('/install_sensorins', methods=["POST"])
# @app.route('/delete_sensorins', methods=["POST"])
# @app.route('/newsensorinfo')
# @app.route('/list_sensor_info_by_loc')
# @app.route('/newsensorinfo_ap')


##################################################################################################################

    


# **************************************** Pymongo *******************************************************

cluster = pymongo.MongoClient('mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority')
db = cluster["Hackathon"]
type_info = db["sensor_type_info"]
ins_info = db["sensor_instance_info"]


############################################################################################################

def initi():
    # all = ins_info.find()
    # for i in all:
    #     topic_n = str(i["_id"])
    #     # os.system("gnome-terminal -x python3 Sensors/" + topic_n+"_sensor.py")

    #     os.system("gnome-terminal --title=" +topic_n +" -x python3 " + "Sensors/"+topic_n+"_sensor.py")
    all = ins_info.find()
    for i in all:
        topic_n = str(i["_id"])
        # os.system("gnome-terminal -x python3 Sensors/" + topic_n+"_sensor.py")

        # os.system("gnome-terminal --title=" +topic_n +" -x python3 " + "Sensors/"+topic_n+"_sensor.py")
        
        q1 = {"sensor_type":str(i["sensor_type"])}
        ab = type_info.find(q1)

        for x in ab:
            d_type = x["output_type"]
        
        os.system("python3 sensor_generator.py "+str(topic_n)+" "+str(d_type))





#########################################################################################################


app = Flask(__name__)
app.config['SECRET_KEY'] = "dub_nation"

@app.route("/")
@cross_origin()
def home():
    '''
    Loads Html which contains forms for Adding and Deleting Sensor Instances.
    '''
    
    try:
        print(request.args['jwt'])
        token = request.args['jwt']
        print("HI")

        #data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        #print(data)
        return render_template("installsensor.html",
            home=SERV[CONST["VM_MAPPING"]["APP"]] + str(CONST["PORT"]["APP_PORT"]) + CONST["ENDPOINTS"]["APP_MANAGER"]["home"],
            ctrl_url = SERV[CONST["VM_MAPPING"]["CONTROLLER"]] + str(CONST["PORT"]["CONTROLLER_PORT"]) + CONST["ENDPOINTS"]["CONTROLLER_MANAGER"]["controller_home"],
            hit_install_type = SERV[CONST["VM_MAPPING"]["SENSOR"]] + str(CONST["PORT"]["SENSOR_PORT"]) + "/install_sensortype",
            hit_install_ins = SERV[CONST["VM_MAPPING"]["SENSOR"]] + str(CONST["PORT"]["SENSOR_PORT"]) + "/install_sensorins"
        )
    except:
        return redirect(SERV[CONST["VM_MAPPING"]["APP"]] + CONST["PORT"]["APP_PORT"] + CONST["ENDPOINTS"]["APP_MANAGER"]["home"])
    


    #type_info.insert_one({"_id":0, "user_name":"Soumi"})
    # return render_template("installsensor.html")
    # return {"Sensor_manager":"IAS"}


# @app.route("/init")
# def init():
    # return redirect("/")

@app.route("/is_sensor_manager_alive")
def is_sensor_manager_alive():
    '''
    Check for sensor Alive Status
    '''
    
    
    # print(list_topics())
    return  {"status":"yes"}


@app.route('/install_sensortype',methods=["POST"])
def install_sensortype():
    '''
    Add Sensor type by Platform Admin
    '''
    
    if request.method=="POST":
        sensor_type=request.form.get("sensor_type")
        output_type=request.form.get("output_type")
    
        q1 = { "sensor_type": sensor_type }

        # mdl = type_info.query.get(sensor_type)
        mdl = type_info.find(q1) 
        alldata=[]
        
        for i in mdl:
            alldata.append(i)
        
        
        ans = "Given Sensor Type Alreaded Present"


        if(len(alldata)==0):
            #model = type_info(sensor_type=sensor_type,output_type=output_type)

            type_info.insert_one({"sensor_type":sensor_type, "output_type":output_type})
            ans = "New Sensor Type Installed Successfully"

    # return redirect("/")
    return render_template("installsensor.html",
            home=SERV[CONST["VM_MAPPING"]["APP"]] + str(CONST["PORT"]["APP_PORT"]) + CONST["ENDPOINTS"]["APP_MANAGER"]["home"],
            ctrl_url = SERV[CONST["VM_MAPPING"]["CONTROLLER"]] + str(CONST["PORT"]["CONTROLLER_PORT"]) + CONST["ENDPOINTS"]["CONTROLLER_MANAGER"]["controller_home"],
            hit_install_type = SERV[CONST["VM_MAPPING"]["SENSOR"]] + str(CONST["PORT"]["SENSOR_PORT"]) + "/install_sensortype",
            hit_install_ins = SERV[CONST["VM_MAPPING"]["SENSOR"]] + str(CONST["PORT"]["SENSOR_PORT"]) + "/install_sensorins",
            type_status = ans
        )




@app.route('/appdev_insert_type/<string:sensor_type>/<string:output_type>')
def appdev_insert_type(sensor_type,output_type):
    '''
    Add Sensor type by Application Manager
    '''
    
    q1 = { "sensor_type": sensor_type }

    # mdl = type_info.query.get(sensor_type)
    mdl = type_info.find(q1) 
    alldata=[]
    
    for i in mdl:
        alldata.append(i)

    if(len(alldata)==0):
        #model = type_info(sensor_type=sensor_type,output_type=output_type)
        type_info.insert_one({"sensor_type":sensor_type, "output_type":output_type})
    ans = {"response":"ok"}
    return ans  

@app.route('/list_of_sensortypes')
def list_of_sensortypes():
    '''
    Lists Sensor types available on Platform
    '''
    
    
    mdl=type_info.find()
    ans=[]
    for x in mdl:
        ans.append(x["sensor_type"])
    
    return {"response":ans}
    

@app.route('/install_sensorins', methods=["POST"])
def install_sensorins():
    '''
    Add Sensor Instance by Platform Admin
    '''
    
    
    if request.method=="POST":
        sensor_type=request.form.get("sensor_type")
        location=request.form.get("location")
        sensor_ip = request.form.get("sensor_ip")
        sensor_port = request.form.get("sensor_port")
    
        # resp=request.get_json()
        # resp = resp['sensor_data'][0]
        # print(resp)
        # sensor_type= resp["sensor_type"]
        # location=resp["location"]
        # sensor_ip=resp["sensor_ip"]
        # sensor_port=resp["sensor_port"]
        ans = "New Sensor Instance Installed Successfully"
        q1={"sensor_type": sensor_type}
        mdl=type_info.find(q1)
        flag=0
        for x in mdl: 
            if(x["sensor_type"]==sensor_type):
                flag=1
                break
        if(flag==1):
            ins_info.insert_one({"sensor_type": sensor_type , "location" : location, "sensor_ip" : sensor_ip, "sensor_port":sensor_port  })
            # ins_info.insert_one(resp)

            all = ins_info.find()
            alldata   = []

            for i in all:
                alldata.append(i)
            d_type = ""
            q1 = {"sensor_type":sensor_type}
            ab = type_info.find(q1)

            for x in ab:
                d_type = x["output_type"]

            print(d_type)
            ins_id = str(alldata[len(alldata)-1]["_id"])
            print(ins_id)
            
            # send_topic = "sensorM_to_sensor"
            # msg = {"topic":ins_id,"d_type":d_type}
            # producer.send(send_topic,msg)
            
            
            # fg=1
            # t = threading.Thread(target=data_producer, args=[ins_id,d_type,fg])
            # t.start()

            os.system("python3 sensor_generator.py "+str(ins_id)+" "+str(d_type))
        else:
            ans = "Invalid Sensor Type"
            
            
             
    # return redirect("/")
    return render_template("installsensor.html",
            home=SERV[CONST["VM_MAPPING"]["APP"]] + str(CONST["PORT"]["APP_PORT"]) + CONST["ENDPOINTS"]["APP_MANAGER"]["home"],
            ctrl_url = SERV[CONST["VM_MAPPING"]["CONTROLLER"]] + str(CONST["PORT"]["CONTROLLER_PORT"]) + CONST["ENDPOINTS"]["CONTROLLER_MANAGER"]["controller_home"],
            hit_install_type = SERV[CONST["VM_MAPPING"]["SENSOR"]] + str(CONST["PORT"]["SENSOR_PORT"]) + "/install_sensortype",
            hit_install_ins = SERV[CONST["VM_MAPPING"]["SENSOR"]] + str(CONST["PORT"]["SENSOR_PORT"]) + "/install_sensorins",
            ins_status = ans
        )
     
    # redirect('/installsensor')            


@app.route('/delete_sensorins', methods=["POST"])
def delete_sensorins():
    '''
    Delete Sensor Instance by Platform Admin
    '''
    
    if request.method=="POST":
        sensor_type=request.form.get("sensor_type")
        location=request.form.get("location")
        
        ins_info.delete_one({"sensor_type":sensor_type,"location":location})
    return redirect("/")
            

@app.route('/newsensorinfo')
def newsensorinfo():
    '''
    {
        "response":[
                        {
                            "location":"hyd",
                            "sensors": [
                                            {
                                                "instances":["1234","2468"],
                                                "sensor_type":"temp"   
                                            },
                                            {
                                                "instances":["4321","6812","6789","1574"],
                                                "sensor_type":"camera"
                                            }
                                        ]
                        }
                    ]
    }
    '''
    
    
    all = ins_info.find()
    alldata   = []

    for i in all:
        alldata.append(i)

    stloc = set()
    stsen = set()

    for x in alldata:
        stloc.add(x["location"])
        stsen.add(x["sensor_type"])

    stloc = list(stloc)
    stsen = list(stsen)
    ans = {}
    loc_info=[]

    for loc in stloc:
        diction=dict()
        diction["location"]=loc
        diction["sensors"]=[]
        for x in alldata:
            if(x["location"]!=loc):
                continue
            else:
                sense=x["sensor_type"]
                flag=0
                for y in diction["sensors"]:
                    if(y["sensor_type"]==sense):
                        y["instance"].append(str(x["_id"]))
                        flag=1
                        break

                if flag == 0 :
                    diction["sensors"].append({"sensor_type" : sense ,"instance" : [str(x["_id"])]})
        loc_info.append(diction)
    for x in loc_info:
        for y in stsen:
            flag=0
            for z in x["sensors"]:
                if(z["sensor_type"]==y):
                    flag=1
                    break
            if flag==0:
                x["sensors"].append({"sensor_type": y ,"instance" : []})


    print(loc_info)
    

    
    return {"response":loc_info}



@app.route('/list_sensor_info_by_loc')
def list_sensor_info_by_loc():
    '''
    {
        "resp": [
            {
                "location": "bakul",
                "sensor_ins": [ "1234", "1246" ],
                "sensor_type": "heat"
            },
            {
                "location": "OBH",
                "sensor_ins": [ "3212", "2246" ],
                "sensor_type": "camera"
            }
        ]
    }
    '''


    all = ins_info.find()
    alldata   = []

    for i in all:
        alldata.append(i)

    #print(alldata[0]["location"])
    stloc = set()
    stsen = set()
    # for i in range(len(alldata)):
    #     stloc.add(alldata[i]["location"])
    #     stsen.add(alldata[i]["sensor_type"])
    for x in alldata:
        stloc.add(x["location"])
        stsen.add(x["sensor_type"])

    stloc = list(stloc)
    stsen = list(stsen)
    ans = {}
    loc_info=[]
    # print(alldata)
    # print(stloc)
    for loc in stloc:
        diction=dict()
        diction["location"]=loc
        diction["sensors"]=[]
        for x in alldata:
            if(x["location"]!=loc):
                continue
            else:
                sense=x["sensor_type"]
                flag=0
                for y in diction["sensors"]:
                    if(y["sensor_type"]==sense):
                        y["instance"].append(str(x["_id"]))
                        flag=1
                        break

                if flag == 0 :
                    diction["sensors"].append({"sensor_type" : sense ,"instance" : [str(x["_id"])]})
        loc_info.append(diction)
    for x in loc_info:
        for y in stsen:
            flag=0
            for z in x["sensors"]:
                if(z["sensor_type"]==y):
                    flag=1
                    break
            if flag==0:
                x["sensors"].append({"sensor_type": y ,"instance" : []})

    print(loc_info)
    final=[]
    for i in range(len(loc_info)):
        loc = loc_info[i]["location"]
        li = loc_info[i]["sensors"] 
        
        for j in li:
            kans = {}
            kans["location"]=loc
            kans["sensor_type"] = j["sensor_type"]
            kans["sensor_ins"] = j["instance"]
            
            final.append(kans)

    return {"resp":final}

@app.route('/newsensorinfo_ap')
def newsensorinfo_ap():

    '''
    {
        "response":"success",
        "sensor_list": [
            {
                "sensor_location": "obh",
                "sensor_type": "camera",
                "sensor_output_type": "array",
                "sensor_instances":2
            },
            {
                "sensor_location": "bakul",
                "sensor_type": "heat",
                "sensor_output_type": "int",
                "sensor_instances":4
            }
        ]
    }
    '''
    
    
    
    all = ins_info.find()
    alldata   = []
    types=type_info.find()
    
    type_to_output=dict()
    for x in types:
        if x["output_type"] not in type_to_output:
            type_to_output[x["sensor_type"]]=x["output_type"]

    for i in all:
        alldata.append(i)

    stloc = set()
    stsen = set()
    
    for x in alldata:
        stloc.add(x["location"])
        stsen.add(x["sensor_type"])

    stloc = list(stloc)
    stsen = list(stsen)
    ans = {}
    loc_info=[]

    for loc in stloc:
        diction=dict()
        diction["location"]=loc
        diction["sensors"]=[]
        for x in alldata:
            if(x["location"]!=loc):
                continue
            else:
                sense=x["sensor_type"]
                flag=0
                for y in diction["sensors"]:
                    if(y["sensor_type"]==sense):
                        y["instance"].append(str(x["_id"]))
                        flag=1
                        break
                        
                if flag == 0 :
                    diction["sensors"].append({"sensor_type" : sense ,"instance" : [str(x["_id"])]})
        loc_info.append(diction)
    for x in loc_info:
        for y in stsen:
            flag=0
            for z in x["sensors"]:
                if(z["sensor_type"]==y):
                    flag=1
                    break
            if flag==0:
                x["sensors"].append({"sensor_type": y ,"instance" : []})
    

    instances=[]
    for x in loc_info:
        for y in x["sensors"]:
            diction=dict()
            diction["sensor_location"]=x["location"]
            diction["sensor_type"]=y["sensor_type"]
            diction["sensor_output_type"]=type_to_output[y["sensor_type"]]
            diction["sensor_instances"]=len(y["instance"])
            instances.append(diction)
    return {"sensor_list" : instances, "response" : "success"}




if(__name__ == "__main__"):
    
    # init_sen()    # Initialize Old Sensors
    
    initi()

    # print(SERV[CONST["VM_MAPPING"]["SENSOR"]])
    # host="0.0.0.0",
    app.run(host="0.0.0.0",port=CONST["PORT"]["SENSOR_PORT"], debug = False)
    
