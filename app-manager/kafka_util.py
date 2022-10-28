from cgitb import enable
import json
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer


CONSTANTS = '' 

with open("constants.json","r") as f:
    CONSTANTS = json.load(f)

KAFKA_SERVER_ADDR = CONSTANTS["KAFKA_HOST_ADDR"]

admin_client = KafkaAdminClient(
    bootstrap_servers = [KAFKA_SERVER_ADDR]
)


def create_topic(topic_name):
    topics = list()
    try:
        topics.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))
        admin_client.create_topics(topics)
        print("Topic created sucessfully")
        return topic_name
    except Exception as e:
        print("============Something went wrong=============", e)
        return None


def delete_topic(topic_name):

    topics = list()
    topics.append(topic_name)
    try:
        admin_client.delete_topics(topics)
        print("Topic deleted sucessfully")
        return True
    except Exception as e:
        print("============Something went wrong=============", e)
        return False


def list_topics():
    try:
        consumer = KafkaConsumer(
            bootstrap_servers = [KAFKA_SERVER_ADDR],
            auto_offset_reset = 'earliest'
        )

        topics = list(consumer.topics())
        for topic in topics:
            print(topic)
        return topics
    except Exception as e:
        print("============Something went wrong=============", e)
        return []


def read_from_topic(topic):
    try:
        # print(topic)
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers = [KAFKA_SERVER_ADDR],
            enable_auto_commit = True,
            consumer_timeout_ms = 5000
        )
        print("consumer made")
        msg_list = list()
        for msg in consumer:
            print(msg)
            msg_list.append(json.loads(msg.value))
            break
        print("message consumed")
        print(msg_list)
        consumer.close()
        return msg_list

    except Exception as e:
        print("============Something went wrong=============", e)
        return []


def post_to_producer(topic_name, msg):
    try:
        producer = KafkaProducer(
            bootstrap_servers = [KAFKA_SERVER_ADDR],
            value_serializer = lambda msg: json.dumps(msg).encode('utf-8')
        )
        producer.send(topic=topic_name, value=msg)
        print("Producer : ", msg)
        return True
    except Exception as e:
        print("============Something went wrong=============", e)
        return False

if __name__ == "__main__":
    list_topics()
    # delete_topic("624f5040fb1a448fdd9cf463")