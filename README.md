# Control dron camera by gaze tracking
Install Python 3.6.12 and requirements.txt modules

From the console

```sh
   python app.py
```

Now the server is running, go to http://127.0.0.1:5000/ to see the webpage

In the Raspberry Pi console run the camera streaming:

```sh
sudo rmmod bcm2835-v4l2
sudo modprobe bcm2835-v4l2
cvlc v4l2:///dev/video0 --v4l2-width 1920 --v4l2-height 1080 --v4l2-chroma h264 --sout '#standard{access=http,mux=ts,dst=0.0.0.0:12345}'
```

Add the RPI IP to the code in WebServer app.py

Again in the RPI start the client in DronMoveCamera app.py

```sh
   python app.py
```