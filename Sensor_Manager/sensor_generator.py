import sys
import os


topic_name = str(sys.argv[1])
d_type = str(sys.argv[2])

with open("Sensors/"+topic_name+"_sensor.py", 'w') as f:

    f.write("from kafka_fun import *")
    # f.write("\n\ncreate_topic('"+ str(topic_name)+"')\n")


    f.write("\n\ndata_producer('"+ str(topic_name)+"','"+str(d_type)+"')")
    

curr_pid = os.system("python " + "Sensors/"+topic_name+"_sensor.py &")
print("Current Process Id for " + topic_name + " = " + str(curr_pid))


