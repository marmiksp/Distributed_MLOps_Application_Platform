FROM python:3
RUN  apt-get update

RUN apt install -y libgl1-mesa-glx

RUN apt install sshpass

RUN apt install zip

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 9200
CMD python aimanager.py