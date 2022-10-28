import sys
import json
import random
import time
import base64

CONST=""
with open("constants.json","r") as f:
    CONST = json.load(f)

# ***************************************** Kafka *********************************************************

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.consumer import KafkaConsumer
from kafka import KafkaProducer

IP_ADDR = CONST["KAFKA_HOST_ADDR"]

def serialize(msg):
        return json.dumps(msg).encode('utf-8')


producer = KafkaProducer(
    bootstrap_servers = [IP_ADDR],
    value_serializer = serialize
)

client = KafkaAdminClient(
    bootstrap_servers = [IP_ADDR]
)

def create_topic(topic_name):

    topics = list()
    try:
        topics.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))
        client.create_topics(topics)
        print("Topic created sucessfully")
        return True
    except:
        print("Already Created or Something went wrong")
        return False

def data_producer(topic,data_type):
    
    # if(fg==1):
    create_topic(topic)
    print("\n\n")
    print("________________________________________________________\n")
    print("                     "+str(topic)+"                     \n")
    print("________________________________________________________\n")
    print("\n")
    producer = KafkaProducer(
        bootstrap_servers = [IP_ADDR],
        value_serializer = serialize
    )
    if(data_type=="int"):
        while True:
            msg = random.randint(10,10000)
            print(msg)
            producer.send(topic,msg)
            # print("Producer : ", msg)
            time.sleep(1)
    elif(data_type == "float"):
        while True:
            msg = int(random.random()*100)/100
            print(msg)
            producer.send(topic,msg)
            # print("Producer : ", msg)
            time.sleep(1)
    elif(data_type == "string"):
        while True:
            digi = random.randint(0,1)
            msg=""
            if(digi%2 == 0):
                msg = "No"
            else:
                msg = "Yes"
            producer.send(topic,msg)
            # print("Producer : ", msg)
            time.sleep(1)
    
    elif(data_type=='array'):
        f=open("data.json")
        data = json.load(f)
        while True:
            i = random.randint(0,4)
            msg=data[str(i)]
            # print(msg)
            producer.send(topic,msg)
            producer.flush(1)
            # print("Producer : ", msg)
            time.sleep(1)
    
    elif(data_type=='image'):
        image_string = []
        for i in range(3):
            with open("cam_images/"+str(i+1)+".jpg", "rb") as image_file:
                image = base64.b64encode(image_file.read())
                image_string.append(image.decode('utf-8'))
        while True:
            # print(type(image_string))
            i = random.randint(0,3)
            # print(len(image_string))
            producer.send(topic,image_string[i])
            # post_to_producer("testing_topic",image_string)
            time.sleep(1)



    elif(data_type=='stream'):
        img_list = []
        for i in range(2):
            with open("videos/listofimg"+str(i+1)+".txt", "r") as image_file:
                img_list.append(image_file.read())

        while True:
            # img_list = []
            # with open("listofimg"+str(i+1)+".txt", "r") as image_file:
            #     img_list = image_file.read()
            i = random.randint(0,1)
            # i = 0
            
                # image_string = image.decode('utf-8')
            # print(type(image_string))
            # print(len(image_string))
            # i = random.randint(0,1)
            # msg=data[str(i)]
            # msgab = np.uint8(msg)
            producer.send(topic,img_list[i])
            # post_to_producer("testing_topic",img_list[i])
            # print(i)
            time.sleep(1)


admin_client = KafkaAdminClient(
    bootstrap_servers = [IP_ADDR]
)     


# ********************************************** INIT Kafka  **********************************************

