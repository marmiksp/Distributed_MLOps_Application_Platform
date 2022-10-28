import json
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.consumer import KafkaConsumer

f = open("./constants.json", 'rb')
constants = json.loads(f)
IP_ADDR = constants['KAFKA_HOST_ADDR']
# IP_ADDR = "0.0.0.0:9092"

client = KafkaAdminClient(
    bootstrap_servers = [IP_ADDR]
)

consumer = KafkaConsumer(
    bootstrap_servers = [IP_ADDR]
)
   

def create_topic(topic_name):

    topics = list()
    # try:
    topics.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))
    client.create_topics(topics)
    print("Topic created sucessfully")
    # return True
    # except:
    print("Something went wrong")
    # return False

def delete_topic(topic_name):

    topics = list()
    topics.append(topic_name)
    # try:
    client.delete_topics(topics)
    print("Topic deleted sucessfully")
    return True
    # except:
    print("Something went wrong")
    return False

def list_topics():

    try:
        topics = list(consumer.topics())
        for topic in topics:
            print(topic)
    except:
        print("Something went wrong")



if __name__=="__main__":
    # init()

    while True:
        optn = int(input("Enter option(create:1, delete:2, list:3): "))

        if optn == 1:
            topic_name = input("Enter topic name to create: ")
            create_topic(topic_name)
        elif optn == 2:
            topic_name = input("Enter topic name to delete: ")
            delete_topic(topic_name)
        elif optn == 3:
            print("Topic list: ")
            list_topics()
        else:
            print("Invalid option")
            break
