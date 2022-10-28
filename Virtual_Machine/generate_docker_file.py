'''
the folder containes all .py files & requirements.txt
the container name for specific module is passed as argument eg:/appmanager
the scriptfile has all run commands to run the folder contents in order
'''


def generate_dockerfile(port, app_path):
    print("=========Making Docker File=========")
    f = open(app_path+"/Dockerfile", "w+")
    f.write("FROM python:3\n\n")
    f.write("RUN  apt-get update\n\n")
    f.write("RUN apt install sshpass\n\n")
    f.write("RUN apt install zip\n\n")
    f.write("WORKDIR /app\n\n")
    f.write("COPY . /app\n\n")
    f.write("RUN pip3 install --no-cache-dir -r requirements.txt\n\n")
    f.write(f"EXPOSE {port}\n\n")
    f.write(f'CMD ["python" ,"run.py", "{port}"]')
    f.close()
    print("==========Docker File made==========")