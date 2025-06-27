import os 
from flask import Flask, app, render_template
from app.utils.camera import VideoCamera


app = Flask(__name__)

@app.route('/')
def page1():
    return render_template('page1.html')


@app.route('/game')
def page2():
    return render_template('page2.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
