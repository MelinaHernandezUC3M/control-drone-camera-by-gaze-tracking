# Import libraries
import time
import socketio
from dron_move_camera import DronMoveCamera

socketio = socketio.Client()

stream_fps = 20
last_update_time = time.time()
wait_time = (1/stream_fps)

dron_camera_movement = DronMoveCamera()
time.sleep(2.0)
dron_camera_movement.start_camera()


@socketio.event
def connect():
    """Connect to server"""
    
    print('[INFO] Connecting to server ', socketio.sid)


@socketio.event
def disconnect():
    """Disconnect from server"""
    dron_camera_movement.stop_camera()
    print('[INFO] Disconnecting from server')
    exit()


@socketio.event
def message(data):
    """Disconnect from server"""
    print('message ', data)


@socketio.on('gaze_position_to_dron', namespace="/dron")
def gaze_position_to_dron(position):
    if position is None:
        return
    
    print('gaze_position_to_dron', position['data'])
    tilt_duty_cycle = position['data']['vertical_movement']
    pan_duty_cycle = position['data']['horizontal_movement']
    dron_camera_movement.set_duty_cycles(pan_duty_cycle, tilt_duty_cycle)
    
    '''
    
    current_time = time.time()
    if current_time - last_update_time > wait_time:
        last_update_time = current_time            
        if gaze_direction == "up":
            dron_camera_movement.up()
        elif gaze_direction == "down":
            dron_camera_movement.down()
        elif gaze_direction == "left":
            dron_camera_movement.left()
        elif gaze_direction == "right":
            dron_camera_movement.right()
    '''



socketio.connect('http://192.168.0.15:5000', namespaces=['/dron'])

while True:
    socketio.sleep(1)
    socketio.emit('gaze_position_result', "Asking for gaze position")
    time.sleep(1)
    

    