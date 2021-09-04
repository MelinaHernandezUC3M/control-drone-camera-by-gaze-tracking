# Control mediante la mirada de una cámara integrada en un dron
Install Python 3.6.12 and requirements.txt modules

From the console

```sh
   python app.py
```

Now the server is running, go to http://127.0.0.1:5000/ to see the webpage

At the same time, a window is opened in the desktop to see how the eyes movement is tracked from the images send by the web app.


en la consola de la pi 

sudo rmmod bcm2835-v4l2
sudo modprobe bcm2835-v4l2
cvlc v4l2:///dev/video0 --v4l2-width 1920 --v4l2-height 1080 --v4l2-chroma h264 --sout '#standard{access=http,mux=ts,dst=0.0.0.0:12345}'

en src del codigo
'http://192.168.0.17:12345/'