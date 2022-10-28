import json
import os
import sys

constants_file = open("constants.json")
constants = json.load(constants_file)

servers_file = open("servers.json")
servers = json.load(servers_file)


def deploy_platform():
    for module in constants["FOLDER_NAME"]:
        ip = servers[constants["VM_MAPPING"][module]]
        ip = str(ip).replace("http://", "").replace(":","")
        username = servers[constants["VM_MAPPING"][module]+"_username"]
        password = servers[constants["VM_MAPPING"][module]+"_password"]
        folder = constants["FOLDER_NAME"][module]

        print(ip, username)

        print("Deploying....." + folder+"\n")
        print("sshpass -p " + password + " sudo scp -r /home/yash/Semester2/IAS/ias-hackathon/" + folder + " " + username + "@" + ip + ":/home/azuresuer/code/ias-hackathon")
        os.system("sshpass -p " + password + " sudo scp -r /home/yash/Semester2/IAS/ias-hackathon/" + folder + " " + username + "@" + ip + ":/home/azureuser/code/ias-hackathon")


def run_platform():

    for module in constants["FOLDER_NAME"]:
        print("\n------BUILDING " + module + " image -------")
        folder = constants["FOLDER_NAME"][module]
        cmd = "sudo docker build -t " + module.lower() + ":latest " + "/home/azureuser/code/ias-hackathon/" + folder
        ssh = "sshpass -p " + servers[constants["VM_MAPPING"][module]+"_password"] + " ssh " + servers[constants["VM_MAPPING"][module]+"_username"] + "@" + str(servers[constants["VM_MAPPING"][module]]).replace("http://","").replace(":","")
        os.system(ssh + " " + cmd)
        print("------BUILD " + module + " image -------\n")

    for images in constants["FOLDER_NAME"]:
        print("\n------EXCUTING " + images + " image -------")
        port = constants["PORT"][images+"_PORT"]
        cmd = "sudo docker run --restart always --name " + images.lower() + " --net=host -d -p " + port + ":" + port + " " + images.lower() + ":latest"
        ssh = "sshpass -p " + servers[constants["VM_MAPPING"][images]+"_password"] + " ssh " + servers[constants["VM_MAPPING"][images]+"_username"] + "@" + str(servers[constants["VM_MAPPING"][images]]).replace("http://","").replace(":","")
        print(ssh + " " + cmd)
        os.system(ssh + " " + cmd)
        print("------EXCUTED " + images + " image -------\n")


def stop_platform():

    for images in constants["FOLDER_NAME"]:
        print("\n------STOPPING " + images + " image -------")
        port = constants["PORT"][images+"_PORT"]
        cmd = "'sudo docker stop $(sudo docker ps -q --filter ancestor="+images.lower()+":latest); sudo docker image remove -f " + images.lower() + "'"
        ssh = "sshpass -p " + servers[constants["VM_MAPPING"][images]+"_password"] + " ssh " + servers[constants["VM_MAPPING"][images]+"_username"] + "@" + str(servers[constants["VM_MAPPING"][images]]).replace("http://","").replace(":","")
        os.system(ssh + " " + cmd)
        # print(ssh + " " + cmd)
        print("------STOPPED " + images + " image -------\n")


if __name__=="__main__":
    if sys.argv[1] == "1":
        deploy_platform()

    if sys.argv[1] == "2":
        run_platform()

    elif sys.argv[1] == "0":
        stop_platform()