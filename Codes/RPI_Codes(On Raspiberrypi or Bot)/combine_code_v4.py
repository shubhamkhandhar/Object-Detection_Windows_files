# Import packages
import os
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import tensorflow as tf
import argparse
import sys
from reference.pid import PID
import time
import imutils
import RPi.GPIO as GPIO

import threading
from flask import Response
from flask import Flask
from flask import render_template
# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")

camera = PiCamera()
panServo = 27
tiltServo = 17
panAngle = 90
tiltAngle = 90
prev = 0
p = 0
r = 0
move = 0


# Set up camera constants
IM_WIDTH =360
IM_HEIGHT = 270
xmin = 0
ymin = 0
xmax = 0
ymax = 0
#IM_WIDTH = 640    Use smaller resolution for
#IM_HEIGHT = 480   slightly faster framerate

def motor_init():
    global motorPwm
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(6, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT) #enable pin of motor
    motorPwm = GPIO.PWM(21, 1000)
    motorPwm.start(0)

def left():
    GPIO.output(26, False)
    GPIO.output(19, True)
    GPIO.output(13, False)
    GPIO.output(6, True)
##    sleep(tf)
    
def right():
    GPIO.output(26, True)
    GPIO.output(19, False)
    GPIO.output(13, True)
    GPIO.output(6, False)
##    sleep(tf)
    
def forward():
    GPIO.output(26, True)
    GPIO.output(19, False)
    GPIO.output(13, False)
    GPIO.output(6, True)
##    sleep(tf)
    
def reverse():
    GPIO.output(26, False)
    GPIO.output(19, True)
    GPIO.output(13, True)
    GPIO.output(6, False)
##    sleep(tf)

def stop():
    GPIO.output(26, False)
    GPIO.output(19, False)
    GPIO.output(13, False)
    GPIO.output(6, False)
##    sleep(tf)

def driveMotor(dc):
    global motorPwm
    assert dc >=0 and dc <= 100
    ###dutyCycle = angle / 18. + 3.
    motorPwm.ChangeDutyCycle(dc)
######    time.sleep(0.3)

def positionServo(servo,angle):
    
    global prev
    assert angle >=0 and angle <= 180
    pwm = GPIO.PWM(servo, 50)
    pwm.start(prev)
    dutyCycle = angle / 18. + 3.
    pwm.ChangeDutyCycle(dutyCycle)   
    time.sleep(0.3)
    pwm.stop()
    prev = dutyCycle
    time.sleep(0.2)

def mapServo(x,y):
    global move
    y = y//2
    x = round( x/2, 2)
    if(y < 0):
        if(y< -60):
            y = 0
            p.initialize()
        
        tilt = 90 + abs(y)
        positionServo(tiltServo, tilt)
    if(y > 0):
        if(y> 60):
            y = 0
            p.initialize()
        
        tilt = 90 - abs(y)
        positionServo(tiltServo, tilt)
########################################
    if(x > 0):
        if(x > 0.2):
            x = 0
            r.initialize()
            
        driveMotor(50)
        left()
        time.sleep(x)#0.65  x
        stop()
        
    if(x < 0):
        if(x < -0.2):
            x = 0
            r.initialize()
        
        driveMotor(50)###abs(x)
        right()
        time.sleep(abs(x))#0.65  abs(x)
        stop()
        
    if(x >= -0.01 and x<= 0.01):
        stop()


def pid_process(objCoord, centerCoord, motion):
    global p
    global r
    if(motion == 0):         
        # calculate the error
        error = centerCoord - objCoord
        # update the value
        output = p.update(error)
        
    if(motion == 1):
        # calculate the error
        error = centerCoord - objCoord
        # update the value
        output = r.update(error)
    
    return output


def system_init():
    global vs
    global p
    global r
    global panAngle
    global tiltAngle
    print("INITIALISING!!!")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    motor_init()
    GPIO.setup(panServo, GPIO.OUT)
    GPIO.setup(tiltServo, GPIO.OUT)    
    positionServo(panServo, panAngle)
    positionServo(tiltServo, tiltAngle)
    # create a PID and initialize it
    p = PID(0.15, 0.04, 0.02)   #p.value, i.value, d.value
    p.initialize()
    # create a PID and initialize it
    r = PID(0.0017, 0.0001, 0.0002)###(1.0, 0.0 , 0.0) ###
    r.initialize()

# Select camera type (if user enters --usbcam when calling this script,
# a USB webcam will be used)
##camera_type = 'picamera'
# This is needed since the working directory is the object_detection folder.
sys.path.append('..')

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

# Name of the directory containing the object detection module we're using
#MODEL_NAME ='/home/pi/tensorflow1/models/research/object_detection/KJSCE_Model' 
#MODEL_NAME ='ssdlite_mobilenet_v2_coco_2018_05_09'
MODEL_NAME = '/home/pi/tensorflow1/models-master/research/object_detection/KJSCE_Model'

# Grab path to current working directory
CWD_PATH = os.getcwd()
######system_init()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'data','labelmap.pbtxt')
#PATH_TO_LABELS = os.path.join(CWD_PATH,'data','mscoco_label_map.pbtxt')

# Number of classes the object detector can identify
NUM_CLASSES = 1

## Load the label map.
# Label maps map indices to category names, so that when the convolution
# network predicts `5`, we know that this corresponds to `airplane`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)


# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize camera and perform object detection.
# The camera has to be set up and used differently depending on if it's a
# Picamera or USB webcam.

# I know this is ugly, but I basically copy+pasted the code for the object
# detection loop twice, and made one work for Picamera and the other work
# for USB.

### Picamera ###
##if camera_type == 'picamera':
def main_code():
    global camera, outputFrame, lock
    # Initialize Picamera and grab reference to the raw capture
    system_init()
    while True:
        
        ###camera = PiCamera()
        camera.resolution = (IM_WIDTH,IM_HEIGHT)
        camera.framerate = 5
        rawCapture = PiRGBArray(camera, size=(IM_WIDTH,IM_HEIGHT))
        rawCapture.truncate(0)
        # try to keep the object

        for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):

            #t1 = cv2.getTickCount()
            
            # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
            # i.e. a single-column array, where each item in the column has the pixel RGB value
            frame = np.copy(frame1.array)
            frame = imutils.rotate(frame, angle=180)
            frame.setflags(write=1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_expanded = np.expand_dims(frame_rgb, axis=0)

                    
                     # Perform the actual detection by running the model with the image as input
            (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections],
                feed_dict={image_tensor: frame_expanded})
                

            height, width = frame.shape[:2]
            centerX = width//2
            centerY = height//2
            #cv2.circle(frame, (centerX, centerY), 5, (0, 255, 0), -1)
            
            boxes= np.squeeze(boxes)
            max_boxes_to_draw=boxes.shape[0]
            scores=np.squeeze(scores)
            classes = np.squeeze(classes).astype(np.int32)
            num = np.squeeze(num)
            min_score_thresh=0.40
            #print("Box: {0}  Scores: {1}".format(boxes, scores))
            for i in range (min(max_boxes_to_draw, boxes.shape[0])):
                if scores[i] > min_score_thresh and classes[i] == 1 :
                    ymin = (int(boxes[i,0]*height))
                    xmin = (int(boxes[i,1]*width))
                    ymax = (int(boxes[i,2]*height))
                    xmax = (int(boxes[i,3]*width))
                    #print (xmin,ymin,xmax,ymax)
                    obj_center_x = int(xmax+xmin)/2
                    obj_center_y = int(ymax+ymin)/2
                    
    ##                area = (xmax - xmin) * (ymax - ymin)
                    radius = min((xmax-xmin)/2, (ymax-ymin)/2)
                    print("classes= {0}\n".format(classes[i]))
                    cv2.circle(frame, (int(obj_center_x), int(obj_center_y)), int(radius), (255, 0, 255), 2)
                    cv2.circle(frame, (int(obj_center_x), int(obj_center_y)), 5, (0, 0, 255), -1)
                    cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (125, 255, 51), thickness=2)
                    if (radius > 60):
                        driveMotor(60)
                        reverse()
                        time.sleep(0.16)
                        stop()
                        
                    elif (radius < 50):
                        driveMotor(60)
                        forward()
                        time.sleep(0.16)
                        stop()
                    
                    else:
                        stop()
                        
                         
                        opY = pid_process(obj_center_y, centerY, 0)
                        opX = pid_process(obj_center_x, centerX, 1)
                        mapServo(opX, opY)
                           #working()
        ##                print("[INFO] center->{0}\n".format(centerX))
        ##                print("[INFO] object->{0}\n".format(obj_center_x))
        ##                
                    
            #cv2.putText(frame,"FPS: {0:.2f}".format(frame_rate_calc),(30,50),font,1,(255,255,0),2,cv2.LINE_AA)

            # All the results have been drawn on the frame, so it's time to display it.
            #cv2.imshow('Object detector', frame)
##
##            t2 = cv2.getTickCount()
##            time1 = (t2-t1)/freq
##            frame_rate_calc = 1/time1
##
##            # Press 'q' to quit
##            if cv2.waitKey(1) == ord('q'):
##                break

            rawCapture.truncate(0)
            # acquire the lock, set the output frame, and release the
            # lock
            with lock:    
                outputFrame = frame.copy()


def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/execute_stop_ml", methods=['GET'])
def working2():
    print("stopping ml and restarting server")
    pid = os.getpid()
    os.system("sudo kill " + str(pid))
    return render_template('index.html')

# 
# @app.route("/<direction>")
# def switch(direction):
#     if (direction == 'Stop '):
#         
#         # return the response generated along with the specific media
#         # type (mime type)
#         pid = os.getpid()
#         os.system("sudo kill " + str(pid))
#         
# #     return render_template('index.html')
# 
# 
# @app.route("/<servo>/<angle>")
# def revert(servo,angle):
#     if (servo == 'pan'):
#         return render_template('index.html')
#     
# 
# 
# # check to see if this is the main thread of execution
if __name__ == '__main__':
# start a thread that will perform motion detection
    t = threading.Thread(target=main_code)
    t.daemon = True
    t.start()

    # start the flask app
    app.run(host='0.0.0.0', port =2000, debug=True, threaded=True)


camera.close()
cv2.destroyAllWindows()

