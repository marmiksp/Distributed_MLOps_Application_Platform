import json
import os
import zipfile

def read_json(file_name):
    '''
    reads json file
    '''
    with open(file_name, "r") as f:
        return json.load(f)



def allowed_file(filename):
    '''
    checks if file is zip
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set(["zip"])


def unzip_file(file_name):
    '''
    unzips the file to folder of same name
    '''
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(file_name))


def check_appname(app_name, app_list):
    '''
    checks if app name is already present
    '''
    
    if app_name in app_list: 
        return False
    return True



def check_models(app_models, model_list):
    '''
    checks if all models are present in model list by AI Manager
    '''


    for model in app_models:
        if model not in model_list:
            return False
    return True


'''
[
    {
    "sensor_type": "sensor_type_1",
    "sensor_output_type": "some_output_type",
    "sensor_instances": "no.of.instances"
    },
    {
    "sensor_type": "sensor_type_2", 
    "sensor_output_type": "some_output_type",
    "sensor_instances": "no.of.instances"
    }
]
'''

def validate_sensor_config(sensorConfig):
    '''
    validates if "sensor_type" and "sensor_instance" are present
    '''
    content=sensorConfig

    for c in content:
        if (c.keys() != {"sensor_type","sensor_output_type","sensor_instances"}) :
            return False    
   
    return True
   
def sensor_requirement(sensorConfig,sensor_list):
    '''
    list of dictionary of sensor id,location from platform manager if not available
    '''
    sensortypes=[]
    for sensor in sensor_list:
        sensortypes.append(sensor["sensor_type"])

    res = []
    for sensor in sensorConfig:
        if sensor['sensor_type'] not in sensortypes:
            temp=dict()
            temp['sensor_type']=sensor['sensor_type']
            temp['sensor_output_type']=sensor['sensor_output_type']
            res.append(temp)
    
    
    return res.json()

             


def validate_zip(file_name):
    '''
    validates zip file
    '''
    try:
        with zipfile.ZipFile(file_name) as zf:
            zf.testzip()
    except zipfile.BadZipfile:
        return False

    unzip_file(file_name)
    folder_name = os.path.splitext(file_name)[0]

    try:
        app_config_json = read_json(folder_name + "/app_config.json")
        sensor_config_json = read_json(folder_name + "/sensor_type_config.json")
        controller_config_json = read_json(folder_name + "/controller_type_config.json")
    except FileNotFoundError as e:
        return {
            'status_code': 500,
            'message': 'Missing file error'
        }

    return {
        "app_config": app_config_json,
        "sensor_type_config": sensor_config_json,
        "controller_type_config": controller_config_json
    }

    # app_name = app_config_json["app_name"]
    # model_temp= app_config_json["model_list"]
    # app_models = []
    # for model in model_temp:
    #     app_models.append(model["model_name"])
    
    # if not check_appname(app_name, app_list):
    #     return '{"status": "400", "message": "App name already present"}'
    
    # if not check_models(app_models, model_list):
    #     return '{"status": "400", "message": "Invalid model list"}'


    # return '{"status": "200", "message": "Valid zip file"}'


# validate_zip("test/App.zip", [], [], [], 'my-app')