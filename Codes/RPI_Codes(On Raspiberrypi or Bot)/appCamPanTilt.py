####    

import os
from time import sleep
from flask import Flask, render_template, redirect, url_for, request, Response, jsonify
from flask_restful import Resource, Api
#from combine_code_v4 import frame

# Raspberry Pi camera module (requires picamera package from Miguel Grinberg)
from camera_pi import Camera

app = Flask(__name__)
api = Api(app)

# Global variables definition and initialization
global panServoAngle
global tiltServoAngle
global state
state = 0
panServoAngle = 90
tiltServoAngle = 90

panPin = 27
tiltPin = 17

@app.route('/')
def index():
    """Video streaming home page."""
 
    templateData = {
        'cam state' : state,
      'panServoAngle'	: panServoAngle,
      'tiltServoAngle'	: tiltServoAngle
	}
    return render_template('index.html', **templateData)


def gen(camera):
    """Video streaming generator function."""
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    global state
    print("inside gen(cam)")
    print(state)
    while state == 0:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/<servo>/<angle>")
def move(servo, angle):
    global panServoAngle
    global tiltServoAngle
    if servo == 'pan':
            if angle == '+':
                    panServoAngle = panServoAngle + 10
                    
                    if(panServoAngle > 150):
                        panServoAngle = 150
                        
            else:
                    panServoAngle = panServoAngle - 10
                    
                    if(panServoAngle < 30):
                        panServoAngle = 30
                        
            os.system("python3 angleServoCtrl.py " + str(panPin) + " " + str(panServoAngle))
    if servo == 'tilt':
            if angle == '+':
                    tiltServoAngle = tiltServoAngle + 10
                    
                    if(tiltServoAngle > 150):
                        tiltServoAngle = 150
            else:
                    tiltServoAngle = tiltServoAngle - 10
                    if(tiltServoAngle < 30):
                        tiltServoANgle = 30
                        
            os.system("python3 angleServoCtrl.py " + str(tiltPin) + " " + str(tiltServoAngle))
    
    templateData = {
  'panServoAngle'	: panServoAngle,
  'tiltServoAngle'	: tiltServoAngle
    }
    return render_template('index.html', **templateData) 
    
@app.route("/<direction>")
def webdrive(direction):
    os.system("python3 Motor_test.py " + str(direction) + " " + str(0.22) + " " + str(50))
    templateData = {
        'cam state' : state,
      'panServoAngle'	: panServoAngle,
      'tiltServoAngle'	: tiltServoAngle
	}
    return render_template('index.html', **templateData)	

@app.route("/execute_start_ml")#(, methods=['GET'])
def working():
    global state
    state = 1
    print("downloading")
    os.system("sudo python3 /home/pi/tensorflow1/models-master/research/object_detection/KJSCE_Model/download_from_dropbox.py")
    os.system("python3 /home/pi/tensorflow1/models-master/research/object_detection/move_graph.py")
    print("downloaded")
    #os.system("python3 /home/pi/tensorflow1/models-master/research/object_detection/combine_code_v5.py")
    #os.chdir('/home/pi/tensorflow1/models-master/research/object_detection')
    print(state)
    #os.system("python3 combine_code_v4.py")
    #os.system(r'export PYTHONPATH=$PYTHONPATH:/home/pi/tensorflow1/models-master/research:/home/pi/tensorflow1/models-master/research/slim')
    #os.system("python3 opencv2_update.py")
    #LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0
    #export PYTHONPATH=/home/pi/.local/lib/python3.7/site-packages/tensorflow:$PYTHONPATH
    #os.system("sudo python3 /home/pi/PanTiltCtrl/testing_sudoname.py")
    print("Detection Stopped")
    state = 0
    print(state)
    #jsonify([{'status':'success'}])
#     templateData = {
#         'cam state' : state,
#         'panServoAngle'	: panServoAngle,
#         'tiltServoAngle'	: tiltServoAngle
#         }
    return jsonify([{'status':'success'}])
    #return redirect(url_for('index'))
    #render_template('index.html', **templateData)
    #jsonify([{'status':'success'}])



if __name__ == '__main__':
    app.run(host='0.0.0.0', port =2000, debug=True, threaded=True)
