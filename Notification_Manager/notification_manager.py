import smtplib
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import requests
import json


app = Flask(__name__)
cors = CORS(app)

app.config['SECRET_KEY'] = "dub_nation"


DB_SERVER = "mongodb+srv://hackathon:hackathon@hackathon.wgs03.mongodb.net/Hackathon?retryWrites=true&w=majority"
client = MongoClient(DB_SERVER)
HACKATHON_DB = client['Hackathon']

AppDB = HACKATHON_DB['AppInfo'] #application info table is set to AppDB
AppInstanceDb = HACKATHON_DB['AppInstance']

req_sess = requests.Session()


def read_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

constants = read_json("constants.json")

@app.route("/send_email", methods=["POST"])
@cross_origin()
def send_email():
    email_details = request.get_json()
    sender = "mlopsseva@gmail.com"
    if "from_email" in email_details:
        sender = email_details["from_email"]
    receiver = email_details['to_email']
    subject = email_details['subject']
    message = email_details['message']
    
    email_text = 'Subject: {}\n\n{}'.format(subject, message)

    try:
        print("smtp object creation")
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        print("smtp object created")
        smtpObj.ehlo()
        print("ehlo done")
        smtpObj.starttls()
        print("starttls done")
        smtpObj.login(sender, "Abc@azureuser")
        print("logged in")
        smtpObj.sendmail(from_addr=sender, to_addrs=[receiver], msg=email_text)
        print("sent email")
        smtpObj.quit()
        print("Successfully sent email")
        return jsonify({'message': 'Email sent successfully', 'status_code': 200}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error sending email', 'status_code': 500}), 500


# @app.route("/send_sms", methods=["POST"])
# @cross_origin()
# def send_sms():
#     pass


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=constants["PORT"]["NOTIFICATION_PORT"])
