import json
import time
from kafka import KafkaProducer


f = open("../constants.json", 'r')
constants = json.loads(f)
IP_ADDR = constants['KAFKA_HOST_ADDR']
# IP_ADDR = "0.0.0.0:9092"


def serialize(msg):
    return json.dumps(msg).encode('utf-8')

producer = KafkaProducer(
    bootstrap_servers = [IP_ADDR],
    value_serializer = serialize
)

l = 10
while l > 0:
    msg = {"message": "Some msg"}
    producer.send('ashish', msg)
    print("Producer : ", msg)
    time.sleep(1.5)
    l -= 1