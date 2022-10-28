from pymongo import MongoClient
import kafka_util
import time, sys


DB_SERVER = "mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority"
client = MongoClient(DB_SERVER)
HACKATHON_DB = client['Hackathon']

ctrl_type_db = HACKATHON_DB['ControllerTypeDB']
ctrl_instance_db = HACKATHON_DB['ControllerInstanceDB']

def run_instance(instance_id):
    try:
        ctrl_instance_doc = ctrl_instance_db.find_one({"_id": instance_id})
        if ctrl_instance_doc:
            while True:
                ctrl_msg_list = kafka_util.read_from_topic(instance_id)
                if ctrl_msg_list and len(ctrl_msg_list) > 0:
                    print(ctrl_msg_list[-1])
                time.sleep(3)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        instance_id = sys.argv[1]
        print("Running controller instance: ", instance_id)
        run_instance(instance_id)
    else:
        print("*******Controller Instance ID is required*******")