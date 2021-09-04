from engineio.payload import Payload
from threading import Lock
from flask import Response, Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import base64
import time
import cv2 as cv
import csv
import glob
import os
import time
from GazeTracking.gaze_tracking import GazeTracking
import numpy as np
from DronVideoStreaming.dron_video_streaming import DronVideoStreaming
from scipy.signal import savgol_filter

gaze = GazeTracking()

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
Payload.max_decode_packets = 500
socketio = SocketIO(app, async_mode=async_mode, ping_timeout=5, ping_interval=1)
thread = None
thread_lock = Lock()
gaze_position = None
list_of_vertical_ratios = []
list_of_horizontal_ratios = []
software_data = []
initial_time = time.time()


def background_thread():
    """Response to check that the server messages are received by the web"""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'background_thread', 'count': count},
                      namespace='/web')


@app.route('/')
def index():
    """Index of the web page"""
    return render_template('index.html', async_mode=socketio.async_mode)


"""DRON NAMESPACE"""


@socketio.on('connect', namespace='/dron')
def connect_dron():
    """Connect to dron application"""
    print('[INFO] dron client connected: {}'.format(request.sid))


@socketio.on('disconnect', namespace='/dron')
def disconnect_dron():
    """Disconnect from dron application"""
    print('[INFO] dron client disconnected: {}'.format(request.sid))

    columns_titles = ['time', 'Gaze Vertical Ratio', 'Servo vertical movement', 'Gaze Horizontal Ratio',
                      'Servo horizontal movement']
    with open('software_data.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns_titles)
        writer.writeheader()
        writer.writerows(software_data)


"""WEB NAMESPACE"""


@socketio.on('connect', namespace='/web')
def connect_web():
    """Connect to web page"""
    print('[INFO] web client connected: {}'.format(request.sid))
    emit('my_response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/web')
def disconnect_web():
    """Disconnect from web page"""
    print('[INFO] web client disconnected: {}'.format(request.sid))


@socketio.on('disconnect_request', namespace='/web')
def disconnect_web_request():
    """Disconnect from web page when requested by the web"""
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.on('webcam_frame', namespace='/web')
def test_message(webcam_image):
    """Get webcam frame and dected gaze direction"""
    global list_of_vertical_ratios
    global list_of_horizontal_ratios
    global software_data
    global gaze_position
    socketio.sleep(0.01)
    encoded_image = webcam_image.split(",")[1]
    nparr = np.fromstring(base64.b64decode(encoded_image), np.uint8)

    # We get a new frame
    frame = cv.imdecode(nparr, cv.IMREAD_COLOR)

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)
    frame = gaze.annotated_frame()

    text = ""
    if gaze.is_right():
        text = "LOOKING RIGTH"
    elif gaze.is_left():
        text = "LOOKING LEFT"
    elif gaze.is_top():
        text = "LOOKING TOP"
    elif gaze.is_bottom():
        text = "LOOKING BOTTOM"
    elif gaze.is_center():
        text = "LOOKING CENTER"

    if gaze.vertical_ratio() is not None:
        list_of_vertical_ratios.append(gaze.vertical_ratio())
    else:
        if len(list_of_vertical_ratios) >= 1:
            list_of_vertical_ratios.append(list_of_vertical_ratios[-1])
        else:
            list_of_vertical_ratios.append(0.94)

    if gaze.horizontal_ratio() is not None:
        list_of_horizontal_ratios.append(gaze.horizontal_ratio())
    else:
        if len(list_of_horizontal_ratios) >= 1:
            list_of_horizontal_ratios.append(list_of_horizontal_ratios[-1])
        else:
            list_of_horizontal_ratios.append(0.665)

    if len(list_of_horizontal_ratios) >= 20 and len(list_of_vertical_ratios) >= 20:
        smooth_list_of_vertical_ratios = savgol_filter(list_of_vertical_ratios, 5, 3)
        smooth_list_of_horizontal_ratios = savgol_filter(list_of_horizontal_ratios, 5, 3)

        sum_vertical_ratios = 0
        for ratio in smooth_list_of_vertical_ratios:
            sum_vertical_ratios += ratio
        print(round(sum_vertical_ratios / len(smooth_list_of_vertical_ratios), 3))

        vertical_movement = gaze.tilt_duty_cycle(smooth_list_of_vertical_ratios[-2])
        horizontal_movement = gaze.pan_duty_cycle(smooth_list_of_horizontal_ratios[-2])

        list_of_vertical_ratios = list_of_vertical_ratios[-20:]
        list_of_horizontal_ratios = list_of_horizontal_ratios[-20:]
    else:
        vertical_movement = gaze.tilt_duty_cycle(list_of_vertical_ratios[-1])
        horizontal_movement = gaze.pan_duty_cycle(list_of_horizontal_ratios[-1])

    message = {"text": text,  "vertical_movement": vertical_movement, "horizontal_movement": horizontal_movement}

    software_data.append({'time': time.time() - initial_time, 'Gaze Vertical Ratio': gaze.vertical_ratio(),
                          'Servo vertical movement': vertical_movement,
                          'Gaze Horizontal Ratio': gaze.horizontal_ratio(),
                          'Servo horizontal movement': horizontal_movement})
    '''
    if len(list_of_horizontal_ratios) >= 20:
        print({'time': time.time() - initial_time, 'Gaze Vertical Ratio': gaze.vertical_ratio(),
                              'Servo vertical movement': vertical_movement,
                              'Gaze Horizontal Ratio': gaze.horizontal_ratio(),
                              'Servo horizontal movement': horizontal_movement})
    '''
    cv.putText(frame, text, (90, 60), cv.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    cv.putText(frame, "Horizontal Ratio:  " + str(gaze.horizontal_ratio()), (90, 130), cv.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv.putText(frame, "Vertical Ratio: " + str(gaze.vertical_ratio()), (90, 165), cv.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv.imshow("Demo", frame)
    cv.waitKey(0)

    gaze_position = message
    emit('gaze_position', {'data': message, 'count': 0})



@socketio.on('gaze_position_result')
def gaze_position_result(data):
    emit('gaze_position_to_dron', {'data': gaze_position}, namespace='/dron')


def encode_video_streaming():
    """Encode dron camera video streaming"""
    stream_link = 'http://192.168.0.14:12345/'
    dron_streaming = DronVideoStreaming(stream_link)
    while True:
        try:
            frame = dron_streaming.get_frame()
            ret, jpeg = cv.imencode('.jpg', frame)
            frame_encoded = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n\r\n')
        except AttributeError:
            pass


@app.route("/dron_camera_streaming")
def dron_camera_streaming():
    """Send dron camera video streaming to the web"""
    return Response(encode_video_streaming(), mimetype="multipart/x-mixed-replace; boundary=frame")


@socketio.on('my_ping', namespace='/web')
def my_ping():
    emit('my_pong')


@socketio.on('my_ping_dron')
def my_ping():
    emit('my_pong', namespace='/dron')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
