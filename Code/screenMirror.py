# CTRL+C TO EXIT THE PROGRAM
# import the necessary packages
from flask import Response
from flask import Flask
from flask import render_template
import threading
import imutils
import cv2
import socket
import pyautogui
import numpy as np

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()

hostname=socket.gethostname()
ipofthehost=socket.gethostbyname(hostname)
# You can assign your desired port, I choose 7856 :)
portbeingused=7856   

# initialize a flask object
app = Flask(__name__)



@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")


def streamscreen():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames 
	
	while True:
		# wait until the lock is acquired

		with lock:
			#Taking screenshot of the screen
			#if you want a region of the screen, you can refer pyautogui documentation
			img = pyautogui.screenshot() 
  
    		# Convert the screenshot to a numpy array 
			frame=np.array(img)
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			#you can resize or leave it.
			#But i recommended to resize as it generally overflows the window
			frame = imutils.resize(frame, width=720)

			outputFrame = frame.copy()
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
	return Response(streamscreen(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':


	# start the flask app
	#You can use host='0.0.0.0' to make it available in local network.
	app.run( host=ipofthehost,port=portbeingused,debug=True,
		 use_reloader=False)
