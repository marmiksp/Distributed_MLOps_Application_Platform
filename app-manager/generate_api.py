import json

def generate_api(model_list, sensor_instances, controller_instances, location, folder, app_name):
    print(folder)
    try:
        constant_file = open("constants.json", "r")
        constants = json.loads(constant_file.read())
        constant_file.close()

        servers_file = open("servers.json", "r")
        servers = json.loads(servers_file.read())
        servers_file.close()

        SENSOR_API = servers[constants["VM_MAPPING"]["APP"]] + constants["PORT"]["APP_PORT"] + constants["ENDPOINTS"]["APP_MANAGER"]["get_sensor_data"]
        MODEL_API = servers[constants["VM_MAPPING"]["APP"]] + constants["PORT"]["APP_PORT"] + constants["ENDPOINTS"]["APP_MANAGER"]["get_model_predict"]
        CONTROLLER_API = servers[constants["VM_MAPPING"]["APP"]] + constants["PORT"]["APP_PORT"] + constants["ENDPOINTS"]["APP_MANAGER"]["send_controller_message"]
        NOTIFICATION_API = servers[constants["VM_MAPPING"]["NOTIFICATION"]] + constants["PORT"]["NOTIFICATION_PORT"] + constants["ENDPOINTS"]["NOTIFICATION_MANAGER"]["send_email"]

        read_sensor_payload = '{ "sensor_instance_id": ins }'
        read_model_payload = '{ "model_name": model_name, "data": data }'
        post_controller_payload = '{ "controller_instance_id": ins, "data": data }'
        notification_payload = '{ "to_email":"ashishrai.game@gmail.com", "subject":subject, "message":message }'
        
        function_code = """
import requests
import openpyxl
import os
import shutil
from openpyxl_image_loader import SheetImageLoader

LOCATION = "{loc}"
SENSOR_API = "{SENSOR_API}"
MODEL_API = "{MODEL_API}"
CONTROLLER_API = "{CONTROLLER_API}"
NOTIFICATION_API = "{NOTIFICATION_API}"

SENSOR_INSTANCE_LIST = {sensor_ins_ids}
MODEL_LIST = {model_list}
CONTROLLER_INSTANCE_LIST = {controller_ins_ids}

def get_sensor_data(sensor_type):
    resp_list=[]
    for idx in SENSOR_INSTANCE_LIST.keys():
        if idx==sensor_type:
            for inst_id in range(len( SENSOR_INSTANCE_LIST[idx])):
                payload = dict()
                payload["sensor_instance_id"] = SENSOR_INSTANCE_LIST[idx][inst_id]
                resp = requests.post(SENSOR_API, json=payload).json()
                resp_list.append(resp["message"])
            break
    return resp_list


def post_controller_message(controller_type, data):
    resp = dict()
    for idx in CONTROLLER_INSTANCE_LIST.keys():
        if idx==controller_type:
            for inst_id in range(len(CONTROLLER_INSTANCE_LIST[idx])):
                payload = dict()
                payload["controller_instance_id"] = CONTROLLER_INSTANCE_LIST[idx][inst_id]
                payload["data"] = data
                resp = requests.post(CONTROLLER_API, json=payload).json()
            break
    return resp

def use_model(model_name, sensor_type):
    data=get_sensor_data(sensor_type)
    resp = dict()
    for idx in range(len(MODEL_LIST)):
        if MODEL_LIST[idx]==model_name:
            if model_name == "firedetect":
                payload = dict()
                payload["model"] = MODEL_LIST[idx]
                payload["data"] = data
                payload["type"] = sensor_type
                resp = requests.post(MODEL_API, json=payload).json()
                break
            else:
                payload = dict()
                payload["model"] = MODEL_LIST[idx]
                payload["data"] = data
                resp = requests.post(MODEL_API, json=payload).json()
                break
    return resp

def pre_process(file_name):
    pxl_doc = openpyxl.load_workbook(file_name)
    sheet = pxl_doc[pxl_doc.sheetnames[0]]

    image_loader = SheetImageLoader(sheet)

    path=os.path.join(os.getcwd(),"dataset")
    os.mkdir(path)
    os.chdir(path)

    for i in range(len(sheet['C'])):
        col='C'+str(i+1)
        image_loader = SheetImageLoader(sheet)
        image = image_loader.get(col)
        name=str(int(sheet[('A'+str(i+1))].value))+"    "+ str(sheet[('B'+str(i+1))].value)+".jpg"
        image.save(name)

    os.chdir("..")
    os.remove(file_name)
    return

def post_process(data):
    shutil.rmtree("dataset")
    return data

def send_notification(subject,message):
    payload = {notification_payload}
    resp = requests.post(NOTIFICATION_API, json=payload).json()
    return resp

        """.format(
            loc=location,
            sensor_ins_ids=sensor_instances,
            controller_ins_ids=controller_instances,
            model_list=model_list,
            SENSOR_API=SENSOR_API,
            MODEL_API=MODEL_API,
            CONTROLLER_API=CONTROLLER_API,
            NOTIFICATION_API = NOTIFICATION_API,
            sensor_payload=read_sensor_payload,
            model_payload = read_model_payload,
            controller_payload = post_controller_payload,
            notification_payload = notification_payload
        )

        path = folder + "/" + app_name
        print(path)
        api_file = open(path + "/api.py", "w+")
        api_file.write(function_code)
        api_file.close()
        print("OK2")

        return True
    except Exception as e:
        print("exception in genrate_api", e)
        return False