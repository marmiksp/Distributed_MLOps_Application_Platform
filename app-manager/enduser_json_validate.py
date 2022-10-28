from pydoc import locate
from werkzeug.utils import secure_filename
import json
import os
import sys
import zipfile

def read_json(file_name):
    '''
    reads json file
    '''
    with open(file_name, "r") as f:
        return json.load(f)


'''
response from Sensor manager
{
    "response": "success",
    "sensor_list": [
        {
            "sensor_location": "some_location_1",
            "sensor_type": "some_type_1",
            "sensor_output_type": "some_output",
            "sensor_instances":"no.of.instances"
        },
        {
            "sensor_location": "some_location_2",
            "sensor_type": "some_type_2",
            "sensor_output_type": "some_output",
            "sensor_instances":"no.of.instances"
        }
    ] 
}
'''

'''
Scheduler
{
    "app_path": "path/to/app",
    "start_time": "some_time",
    "end_time": "some_time",
    "standalone": "true/false"
    "location": "some_location"
}
'''

'''
App
"sensors": [
        {
            "sensor_type": "sensor_type_1",
            "sensor_instances" : "some number of sensor instances"
        }
    ]
'''



def UserSensorValidation(sensor_inf, app_req, app_location):
    '''
    check if we have sensor type ,loc and number of instances of that sensor
    list of dictionary of sensor id,location from platform manager
    '''
    sensor_list=sensor_inf["sensor_list"]
    app_sense=app_req["sensors"]

    flag=0

    for x in app_sense:
        
        type_=x["sensor_type"]
        for y in sensor_list:
            if y["sensor_location"]==app_location and y["sensor_type"]==type_ :
                if int(y["sensor_instances"])<int(x["sensor_instances"]) :
                    flag=1
                    break
    flag2=0
    for x in sensor_list:
        if x["sensor_location"]==app_location:
            flag2=1
            break
    #for x in sensor_list
    count=0
    for x in app_sense:
        for y in sensor_list:
            if x["sensor_type"]==y["sensor_type"] and app_location==y["sensor_location"]:
                count=count+1
    flag3=0
    if(count==len(app_sense)):
        flag3=1


    if flag==0 and flag2==1 and flag3==1:
        return True
    else:
        return False







def validate_app_json(config):
    '''
    validates app config json
    '''
    
    if(config.keys() != {"app_name","start_time","end_time","standalone","location"}):
        return False
    

    return True


def validate_app_config(app_config,sensor_inf,app_location,app_names_list):
    '''
    validates complete end user json
    '''

    if validate_app_json(app_config):
        return '{"status:500","message":"app_config is not valid"}'

    app_name = app_config["app_name"]
    if app_name not in app_names_list:
        return '{"status:500","message":"app_name is not valid"}'

    location = app_config["location"]
    if not UserSensorValidation(sensor_inf, app_config["sensors"], location):
        return '{"status:500","message":"sensor_config is not valid"}'
    
    return '{"status:200","message":"app_config is valid"}'

