# from flask import Flask, render_template
# import sys
# import api
# # from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
# # from flask_apscheduler import APScheduler

# app = Flask(__name__)

# app.config['TEMPLATES_AUTO_RELOAD'] = True
    
# @app.route("/")
# def hello():
#     with app.app_context():
#         print("enter hello")
#         x = []
#         try:
#             x = api.get_sensor_data("camera")
#             print("camera", x)
            
#             x = api.get_sensor_data("smoke")
#             print("smoke", x)
            
#             x = api.get_sensor_data("temperature")
#             print("temperature", x)

#         except Exception as e:
#             print("something went wrong ", e)    
        
#         if x is None or len(x) == 0 :
#             print("\n\n ******************** \n\nkuch nhi \n **************** \n\n")
#             x = [0.0, 0.0, 8.0, 14.0, 16.0, 16.0, 1.0, 0.0, 0.0, 6.0, 16.0, 16.0, 8.0, 3.0, 0.0, 0.0, 0.0, 14.0, 14.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 15.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 8.0, 15.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 13.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 4.0, 0.0, 0.0, 0.0]
        
#         print("enter preprocess")
#         print(x)


#         x = api.pre_process(x)
    
#         # x = [0.0, 0.0, 8.0, 14.0, 16.0, 16.0, 1.0, 0.0, 0.0, 6.0, 16.0, 16.0, 8.0, 3.0, 0.0, 0.0, 0.0, 14.0, 14.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 15.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 8.0, 15.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 13.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 4.0, 0.0, 0.0, 0.0]
#         print("enter use model")
#         x = api.use_model(x, "digit_pred")
#         print("enter post process")
#         x = api.post_process(x)
#         response = {
#             "result":x
#         }
        
#         print("controller time")
#         print(api.post_controller_message("light", "Testing light controller"))
#         print(api.post_controller_message("sprinkler", "Testing light controller"))
#         print(api.post_controller_message("ac", "Testing light controller"))
#         print(api.post_controller_message("control1", "Testing light controller"))
        
#         print("notification time")
#         print(api.send_notification("result printed","hey this is MLOPs seva...testing notification! Hell yeah!!!!"))

	

#         return render_template("index.html", result=response)
    

# if __name__ == "__main__":
#     print(sys.argv[1])
#     app.run(host='0.0.0.0', port=sys.argv[1], debug=True)
#     scheduler = BlockingScheduler()
#     scheduler.add_job(func=hello, trigger='interval', id='job', seconds=9)
#     scheduler.start()
#     # atexit.register(lambda: scheduler.shutdown())
#     # print("hello world")



from flask import Flask,jsonify,render_template, request
from flask_cors import CORS
import api
import sys

app = Flask(__name__)
CORS(app)

def attendance(filename):
    # some logic
    students = []
    
    api.pre_process(filename)
    pred = api.use_model("face_recognition", "camera")
    api.send_notification("Attendance", "Attendance has been updated")


    """
    {
        prediction: {
            name: status
        }
    }
    """

    output = dict(pred['prediction'])

    for i in output.keys():
        students.append({
            "name": i,
            "status": output[i]
        })

    return render_template("attendance.html", students=students)

@app.route('/')
def Index():
    return render_template("index.html", attendance="/attendance", attentiveness="/SentimentAnalysis" , classroom_peripheral_control="/MotionDetect", smoke_detector="/firedetection")

@app.route("/firedetection")
def home():
    return render_template('alarmsystem.html')

@app.route("/SentimentAnalysis")
def MotionDetect():
    return render_template("home.html")

@app.route('/MotionDetect')
def SentimentAnalysis():
    return render_template("index2.html")

@app.route('/attendance')  
def upload():  
    return render_template("menu.html")  
                

@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':
        print("getting files from request now")  
        f = request.files['file']  
        print("saving the file now")
        f.save(f.filename)  
        print("saved the file")
    # return render_template("success.html", name = f.filename) 
    return attendance(f.filename)

@app.route('/firedetect')
def detectFire():
    temp_sensor = api.use_model("firedetect", "temperature")
    smoke_sensor = api.use_model("firedetect", "smoke")
    api.post_controller_message("sprinkler", temp_sensor["prediction"])
    api.post_controller_message("alarm",smoke_sensor["prediction"])
    if temp_sensor["prediction"] == "Start sprinklers!!":
        api.send_notification("Fire", "Fire detected.. Sprinklers started")
    else:
        api.send_notification("Fire", "Fire undetected.")
    if smoke_sensor["prediction"] == "FIREEE!!!!":
        api.send_notification("Fire", "Smoke Detected.. Alarm is ON")
    else:
        api.send_notification("Fire", "No smoke")
    return jsonify({'temperature':temp_sensor, "smoke":smoke_sensor})

@app.route("/sentiment")
def sentiment():
    resp=api.use_model("detect_expression","camera")
    api.post_controller_message("indicator", resp["prediction"])
    if resp["prediction"] == "green":
        api.send_notification("Attentiveness", "Class is attentive")
    else:
        api.send_notification("Attentiveness", "Class is not attentive")
    return jsonify(resp["emotion_count"])

@app.route('/motiondetection')
def motiondetection():
    x = api.use_model("motiondetection","video")
    str="No Motion"
    if x["prediction"]==1:
        api.post_controller_message("light", "ON")
        api.post_controller_message("fan", "SPEED 5")
        str="Motion Detected"
        api.send_notification("Motion", "Motion is Detected.")

    else:
        api.post_controller_message("light", "OFF")
        api.post_controller_message("fan", "SPEED 0")
        api.send_notification("Motion", "Motion is not detected")
    
    return str


if __name__=="__main__":
    app.run(host="0.0.0.0", port=sys.argv[1], debug=True)
