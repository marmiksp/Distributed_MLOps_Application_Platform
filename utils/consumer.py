import json
from kafka import KafkaConsumer



f = open("../constants.json", 'r')
constants = json.loads(f)
IP_ADDR = constants['KAFKA_HOST_ADDR']
# IP_ADDR = "0.0.0.0:9092"


consumer = KafkaConsumer(
    "ashish",
    bootstrap_servers = [IP_ADDR],
    auto_offset_reset = 'earliest'
)

for msg in consumer:
    print(json.loads(msg.value))