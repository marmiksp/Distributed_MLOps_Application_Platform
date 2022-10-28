import json
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer


KAFKA_SERVER_ADDR = "13.71.94.55:9092"

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
            topics=topic,
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
        consumer = KafkaConsumer(
            topics=topic,
            bootstrap_servers = [KAFKA_SERVER_ADDR],
            auto_offset_reset = 'earliest'
        )

        msg_list = list()
        for msg in consumer:
            print(json.loads(msg.value))
            msg_list.append(json.loads(msg.value))
        
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

