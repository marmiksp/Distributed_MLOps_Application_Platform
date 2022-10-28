import json,shutil,os
f = open('constants.json')
# constant_data = json.load(f)
s = open('servers.json')
json_data = json.load(s)
data = json.load(f)

dict={
    "SENSOR":"Sensor_Manager",
    "MODEL": "AI_Manager",
    "LOAD": "LoadBalancer",
    "APP": "app-manager",
    "DEPLOYER": "Deployer",
    "NODE": "NodeManager",
    "SCHEDULER":"Scheduler",
    "AUTH":"Auth_Manager",
    "NOTIFICATION": "Notification_Manager",
    "CONTROLLER": "Controller_Manager",
    "VM1":"Virtual_Machine"
    }

for service in data['LIST']:
    port = data["PORT"][service+"_PORT"]
    filename = data["FILES"][service+"_FILE"]
    destination = "./"+dict[service]
    print(destination)
    shutil.copy('constants.json',destination)
    shutil.copy('servers.json',destination)
    cmd="python3 docker_file_generator.py "+port+" "+destination+" "+filename
    os.system(cmd)

# os.system(f"zip -r Virtual_Machine.zip Virtual_Machine")

# os.system(f"sshpass -p Abc@azureuser ssh -o StrictHostKeyChecking=no azureuser@{json_data['vm2']} 'whoami;sudo apt-get update;whoami;sudo apt install -y docker.io ;whoami;sudo apt install -y sshpass'")

# os.system(f"sshpass -p 'Abc@azureuser' scp -o StrictHostKeyChecking=no Virtual_Machine.zip azureuser@{json_data['vm2']}:/home/azureuser")

# os.system(f"sshpass -p Abc@azureuser ssh azureuser@{json_data['vm2']} 'cd /home/azureuser/;unzip Virtual_Machine.zip;cd Virtual_Machine;sudo docker build -t vmimage:latest .;sudo docker run --net=host -it -d -p {constant_data['PORT']['VM1_PORT']}: {constant_data['PORT']['VM1_PORT']} vmimage' ")



