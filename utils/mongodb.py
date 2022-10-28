from pymongo import MongoClient

DB_SERVER = "mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority"
client = MongoClient(DB_SERVER)
HACKATHON_DB = client['Hackathon']


def delete_db(dbName):
    try:
        HACKATHON_DB.drop_collection(dbName)
        print("{} Database deleted sucessfully".format(dbName))
    except:
        print("Something went wrong for DB {}".format(dbName))
    

if __name__ == "__main__":
    
    # delete_db('AppInfo')
    delete_db('Scheduler_db')
    # delete_db('AppInstance')
    # delete_db('ModelDB')
    # delete_db('Node_db')
    # delete_db('Scheduler_db')
    # delete_db('sensor_instance_info')
    # delete_db('sensor_type_info')
