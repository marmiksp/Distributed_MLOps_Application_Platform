from asyncore import read
import os,sys,json
'''
the folder containes all .py files & requirements.txt
the container name for specific module is passed as argument eg:/appmanager
the scriptfile has all run commands to run the folder contents in order
'''
def generate_dockerfile(port,folder,file):
    f=open(folder+"/Dockerfile","w")
    destination="/app"
    f.write("FROM python:3\n")
    f.write("RUN  apt-get update\n\n")
    f.write("RUN apt install -y libgl1-mesa-glx\n\n")
    f.write("RUN apt install sshpass\n\n")
    f.write("RUN apt install zip\n\n")
    f.write("WORKDIR /app\n")
    # entries=os.listdir(os.getcwd())
    f.write("COPY . /app\n")
    # for filename in entries:
    #     if filename=="Dockerfile":
    #         continue
    #     f.write("COPY "+filename+" "+destination+"/\n")
    f.write("RUN pip install -r requirements.txt\n")
    # f.write("COPY "+data['appfolderpath']+" "+data['appfolderpath']+"/image\n")
    f.write("EXPOSE "+port+"\n")
    # f.write("ENTRYPOINT [./]\n")

    # '''generate_script_file()'''
    # sfile=open("scriptfile.sh","w")
    # sfile.write("#!/bin/bash\n")
    # for cmd in data['listOffiles']:
    #     sfile.write("python3 "+cmd+"\n")
    # f.write("RUN chmod +x scriptfile.sh\n")    
    f.write("CMD python "+file)

    # if os.path.exists("scriptfile.sh"):
    #     os.remove("scriptfile.sh")
    # else:
    #     print("The file does not exist")
    
generate_dockerfile(sys.argv[1],sys.argv[2],sys.argv[3])




