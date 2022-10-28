import requests
from flask import Flask, redirect, render_template, session, jsonify, request, url_for
from pymongo import MongoClient
from flask_session import Session
from sqlalchemy import false
from werkzeug.utils import secure_filename
import json
import app_zip_validate as azv
import enduser_json_validate as ejv
import kafka_util, file_storage, generate_api, dockerfile_generator
import os
import zipfile
from flask_cors import CORS, cross_origin
import jwt
import shutil
import zipfile


app = Flask(__name__)
cors = CORS(app)

app.config['SECRET_KEY'] = "dub_nation"


DB_SERVER = "mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority"
client = MongoClient(DB_SERVER)
HACKATHON_DB = client['Hackathon']

AppDB = HACKATHON_DB['AppInfo'] #application info table is set to AppDB
AppInstanceDb = HACKATHON_DB['AppInstance']

sess = Session(app)
req_sess = requests.Session()

SENSOR_PORT = 9100
MODEL_PORT = 9200
PLATFORM_PORT = 9300
APP_PORT = 9400
DEPLOYER_PORT = 9500
NODE_PORT = 9500
SCH_PORT = 9600



def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

constants = read_json("constants.json")
servers = read_json("servers.json")


def unzip_file(file_name,source_folder):
    '''
    unzips the file to folder of same name
    '''
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(source_folder)


@app.route("/")
@cross_origin()
def hello():
    return render_template("landing_page.html", 
        login=servers[constants["VM_MAPPING"]["AUTH"]] + str(constants["PORT"]["AUTH_PORT"]) + constants["ENDPOINTS"]["AUTH_MANAGER"]["login"],
        register=servers[constants["VM_MAPPING"]["AUTH"]] + str(constants["PORT"]["AUTH_PORT"]) + constants["ENDPOINTS"]["AUTH_MANAGER"]["register"],
        data_scientist=servers[constants["VM_MAPPING"]["MODEL"]] + str(constants["PORT"]["MODEL_PORT"]) + constants["ENDPOINTS"]["AI_MANAGER"]["ai_home"],
        admin=servers[constants["VM_MAPPING"]["SENSOR"]] + str(constants["PORT"]["SENSOR_PORT"]) + constants["ENDPOINTS"]["SENSOR_MANAGER"]["admin"],
        developer=servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["developer"],
        user=servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["user"]
    )


@app.route("/developer")
def dev():
    try:
        print(request.args['jwt'])
        token = request.args['jwt']
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        return render_template("appdeveloper.html",
            home=servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["home"],
            get_available_resources = servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["get_available_resources"],
            upload_url = servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["upload_application"]
        )
    except:
        return redirect("/")


@app.route("/enduser")
@cross_origin()
def enduser():
    try:
        print(request.args['jwt'])
        token = request.args['jwt']
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        return render_template("enduser.html",
            home=servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["home"],
            get_app_list = servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["get_app_list"],
            deploy_app = servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["deploy_app"]
        )
    except:
        return redirect("/")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in set(["zip"])


@app.route("/get_sensor_data", methods=["POST"])
def get_sensor_data():
    print("in get sensor data of app manager")
    req = request.get_json()
    print("request came")
    sensor_instance_id = req["sensor_instance_id"]
    print("sensor instance detected")
    msg = kafka_util.read_from_topic(sensor_instance_id)
    print("message = {}".format(msg))
    return jsonify({"message" : msg[-1]})


@app.route("/get_model_predict", methods=["POST"])
def get_model_predict():
    req = request.get_json()
    print(req)
    resp = requests.post(servers[constants["VM_MAPPING"]["MODEL"]] + str(constants["PORT"]["MODEL_PORT"]) + constants["ENDPOINTS"]["AI_MANAGER"]["get_prediction"], json=req).json()
    return resp


@app.route("/send_controller_message", methods=["POST"])
def send_controller_message():
    try:
        print("Sending data to controller")
        req = request.get_json()
        print(req)
        kafka_util.post_to_producer(req["controller_instance_id"], req["data"])
        return jsonify({"message" : "Successfully sent the message", "status_code" : 200}), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Failed to send the message", "status_code" : 500}), 500



def get_sensor_instances(app_name, sensors, location):
    app_info = AppDB.find_one({ 'app_name': app_name })
    sensors_list = req_sess.get(servers[constants["VM_MAPPING"]["SENSOR"]] + str(constants["PORT"]["SENSOR_PORT"]) + constants["ENDPOINTS"]["SENSOR_MANAGER"]["list_sensor_info_by_loc"]).json()
    print(sensors_list)
    sensor_instance_list = list()
    final_instances = dict()

#filter by locaion
    for obj in sensors_list['resp']:
        if obj['location'] == location:
            sensor_instance_list.append(obj)

    total_added = 0
    for sensor in sensors:
        for ins in sensor_instance_list:
            if(ins['sensor_type'] == sensor['sensor_type']):
                if len(ins['sensor_ins']) == 0:
                    return jsonify({ 'status_code': 500, 'message': 'No sensors available' })
                else:
                    for i in ins['sensor_ins']:
                        if ins['sensor_type'] not in final_instances:
                            final_instances[ins['sensor_type']] = list()
                        if i not in final_instances[ins['sensor_type']]:
                            final_instances[ins['sensor_type']].append(i)
                            total_added += 1
    
    return {'status_code': 200, 'final_instances': dict(final_instances)}


def get_controller_instances(app_name, controllers, location):
    resp = req_sess.post(servers[constants["VM_MAPPING"]["CONTROLLER"]] + str(constants["PORT"]["CONTROLLER_PORT"]) + constants["ENDPOINTS"]["CONTROLLER_MANAGER"]["get_controller_instance_details_by_location"], json={ 'location': location }).json()
    controller_instance_list = resp["response"]
    print(controller_instance_list, "=====================", controllers)
    final_instances = dict()

    total_added = 0
    for type in controllers:
        added = False
        for ctrl in controller_instance_list:
            if added ==True:
                break
            if ctrl["ctrl_type"] == type["controller_type"]:
                for ins in ctrl["ctrl_instance_list"]:
                    if ctrl["ctrl_type"] not in final_instances:
                        final_instances[ctrl["ctrl_type"]] = list()

                    if ins["ctrl_instance_id"] not in final_instances[ctrl["ctrl_type"]]:
                        final_instances[ctrl["ctrl_type"]].append(ins["ctrl_instance_id"])
                        added = True
                        total_added += 1
                        # break

    print(final_instances)
    return {'status_code': 200, 'final_instances': dict(final_instances)}


def generate_api_file(model_list, sensor_instances, controller_instances, location, folder, app_name):

    print(model_list, sensor_instances,controller_instances, location, folder, app_name)
    if (generate_api.generate_api(model_list, sensor_instances, controller_instances, location, folder, app_name)):
        # dockerfile_generator.generate_docker_file(folder)
        # os.system('docker build -t '+ app_name + ':latest' + folder+'/Dockerfile')
        # os.system('docker save '+app_name+':latest | gzip > '+app_name+'_latest.tar.gz')

        # file_storage.upload_file('docker_image', app_name+'_latest.tar.gz', app_name+'_latest.tar.gz')
        
        id = AppInstanceDb.insert_one({
            "location": location,
            # "docker_image": app_name+'_latest.tar.gz'
            "docker_image": folder+'/'+app_name,
            "node_id" : None,
        })

        # app_ins_id = str(AppInstanceDb.find_one({
        #     "location": location,
        #     # "docker_image": app_name+'_latest.tar.gz'
        #     "docker_image": folder+'/'+app_name,
        # })['_id'])


        print(id.inserted_id)

        return str(id.inserted_id)
    else:
        return None




#USER

@app.route("/get_app_list", methods=["GET"])
def get_app_list():
    '''
    gets available app list from app database
    '''
    app_list = AppDB.find()
    app_list_json = []
    for app in app_list:
        app_list_json.append({
            "app_id": str(app['_id']),
            "app_name": app['app_name']})

    return jsonify(app_list_json)


@app.route("/deploy_app", methods=['POST'])
def deploy_app():
    '''
    Sends app deployment info to Scheduler
    '''
    req = request.get_json()
    print(req)

    app_name = req["app_name"]
    location = req["location"]
    start_time= req["start_time"]
    duration= req["duration"]
    standalone = req["standalone"]

    if not os.path.exists(app_name):
        zip_name = app_name + ".zip"
        file_storage.download_file("Application_Package", zip_name, zip_name)
        unzip_file(zip_name, os.getcwd())
        os.remove(zip_name)

    app = AppDB.find_one({ 'app_name': app_name })
    if app == None:
        return jsonify({ "status_code": 500, "message": "App does not exist." })
    print(app)

    print("$$$$$$$$$$$$$$$$$$$$",app_name, app["sensors"], location)
    sensor_instances_list = get_sensor_instances(app_name, app['sensors'], location)
    print("####################",sensor_instances_list)
    if sensor_instances_list['status_code'] == 500:
        return jsonify({
            "status_code": 500,
            "message": sensor_instances_list["message"]
        })
    else:
        sensor_instances_list = sensor_instances_list["final_instances"]

    controller_instances_list = get_controller_instances(app_name, app["controllers"], location)
    if controller_instances_list['status_code'] == 500:
        return jsonify({
            "status_code": 500,
            "message": controller_instances_list["message"]
        })
    else:
        controller_instances_list = controller_instances_list["final_instances"]
    
    app_inst_id = generate_api_file(app['models'], sensor_instances_list, controller_instances_list, location, os.getcwd(), app_name) # Make Folder and appname dynamic
    print("********************",app_inst_id)
    # file_storage.download_file("Application_Package", app_name+'_latest.tar.gz', app_name+'.zip')

    if app_inst_id == None:
        return jsonify({
            "status_code": 500,
            "message": "unable to deploy"
        })
    
    # zip_ref = zipfile.ZipFile("Test1.zip")
    # dir_name = "temp/"
    # os.mkdir(dir_name, mode=0o777)
    # os.chdir(dir_name)
    # zip_ref.extractall(dir_name)
    # zip_ref.close()
    # os.chdir("../")

    # os.system("")

    print(os.getcwd())
    shutil.make_archive(app_inst_id, 'zip', os.getcwd() + "/" + app_name)
    file_storage.upload_file("Applications_Docker_Image", app_inst_id + ".zip", app_inst_id + ".zip")
    os.remove(app_inst_id + ".zip")

    payload = {
        "app_inst_id" : app_inst_id,
        "start_time": start_time,
        "end_time": duration,
        "stand_alone": standalone #bool
    }
    #change with kafka
    response = req_sess.post(servers[constants["VM_MAPPING"]["SCHEDULER"]] + str(constants["PORT"]["SCHEDULER_PORT"]) + constants["ENDPOINTS"]["SCHEDULER_MANAGER"]["deploy_app"], json=payload) 
    return {
        "status_code": 200,
        "message": response.json()
    }


#DEV
@app.route("/get_available_resources", methods=['GET'])
def get_available_resources():
    """
    This will return the available Models, Sensors type, and Controllers
    """
    resp = {
        "models": list(),
        "sensors": list(),
        # "controllers": list()
    }

    model_uri = servers[constants["VM_MAPPING"]["MODEL"]] + str(constants["PORT"]["MODEL_PORT"]) + constants["ENDPOINTS"]["AI_MANAGER"]["get_model_list"]
    sensor_uri = servers[constants["VM_MAPPING"]["SENSOR"]] + str(constants["PORT"]["SENSOR_PORT"]) + constants["ENDPOINTS"]["SENSOR_MANAGER"]["sensor_info"]
    controller_uri = servers[constants["VM_MAPPING"]["CONTROLLER"]] + str(constants["PORT"]["CONTROLLER_PORT"]) + constants["ENDPOINTS"]["CONTROLLER_MANAGER"]["get_controller_list"]

    model_list = req_sess.get(model_uri).json()
    resp["models"] = model_list

    sensor_info_list = req_sess.get(sensor_uri).json()
    resp["sensors"] = sensor_info_list

    controller_list = req_sess.get(controller_uri).json()
    resp["controllers"] = controller_list

    print(resp)
    return resp


@app.route("/upload_application", methods=["POST"])
def upload_application():
    '''
    This will allow App Developer to upload their zip file containing
    Applications related files: 
        app_config.json, sensor_type_config.json, controller_type.json
        source code, requirements.txt as App.zip

    '''

    resp = dict()

    # if 'file' not in request.files:
    #     resp = {"status_code":400, 'message': 'No file part in the request'}
    #     return resp

    file = request.files['file']

    # if file.filename == '':
    #     resp = {"status_code":400, 'message': 'No file selected for uploading'}
    #     return resp
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        resources = get_available_resources()
        print(file.filename)
        file.save(file.filename)


        config = azv.validate_zip(file.filename)

        model_uri = servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["get_app_list"]
        existing_app_list = req_sess.get(model_uri).json()

        print(existing_app_list)

        for a in existing_app_list:
            if a['app_name'] == config['app_config']['app_name']:
                return jsonify({"status_code":400, 'message': 'App already exists'})

        models_list = list()
        print(config['app_config']['model_list'], "\n", resources["models"]["model_list"])
        for m in config['app_config']['model_list']:
            for n in resources["models"]["model_list"]:
                if(m['model_name'] == n):
                    models_list.append(n)

        if len(models_list) != len(config['app_config']['model_list']):
            return jsonify({"status_code":400, 'message': 'Model does not exist'})

        ##h------------------

        app_name = config['app_config']['app_name']
        print(app_name)
        file_storage.upload_file("Application_Package", app_name+'.zip', file.filename)

        app_info = {
            "app_name": config['app_config']['app_name'],
            "app_author": config['app_config']['app_author'],
            "models": models_list,
            "sensors": config['sensor_type_config'],
            "controllers": config['controller_type_config']
        }

        AppDB.insert_one(app_info)

        resp = {
            "status_code": 200,
            'message': 'File successfully uploaded'
        }
    else:
        resp = {"status_code":400, 'message': 'Allowed file types are zip'}
    os.remove(file.filename)
    return redirect (servers[constants["VM_MAPPING"]["APP"]] + str(constants["PORT"]["APP_PORT"]) + constants["ENDPOINTS"]["APP_MANAGER"]["home"])


if(__name__ == "__main__"):
    app.run(host='0.0.0.0', port=constants["PORT"]["APP_PORT"], debug=True)
