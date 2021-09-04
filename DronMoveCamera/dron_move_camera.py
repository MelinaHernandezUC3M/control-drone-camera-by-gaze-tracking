import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import tkinter as tk


class DronMoveCamera(object):
    def __init__(self):        
        self._duty_cycle_tilt = 7
        self._duty_cycle_pan = 2
        #self._camera = camera = PiCamera()
        
        # Set GPIO numbering mode
        GPIO.setmode(GPIO.BOARD)

        # Set pins 11 & 12 as outputs, and define as PWM tilt_servo & pan_servo
        GPIO.setup(12,GPIO.OUT)
        self._pan_servo = GPIO.PWM(12,50) # pin 11 for servo1
        GPIO.setup(11,GPIO.OUT)
        self._tilt_servo = GPIO.PWM(11,50) # pin 12 for servo2
        print("set up gpio")
        print(self._tilt_servo)
        
        self._pan_servo.start(self._duty_cycle_pan)
        self._tilt_servo.start(self._duty_cycle_tilt)
        time.sleep(0.3)
        self._pan_servo.ChangeDutyCycle(0)
        self._tilt_servo.ChangeDutyCycle(0)
        time.sleep(0.7)
    
    def start_camera(self):
        # Start camera        
        #self._camera.start_preview(fullscreen=False,window=(100,200,300,400))
        
        # Start PWM running on both servos, value of 0 (pulse off)
        #self._pan_servo.start(self._duty_cycle_pan)
        #self._tilt_servo.start(self._duty_cycle_tilt)

        print("Setup camera and servos")
    
    def set_duty_cycles(self, pan_duty_cycle, tilt_duty_cycle):
        if tilt_duty_cycle == None or tilt_duty_cycle == self._duty_cycle_tilt:
            self._duty_cycle_tilt = 0
        else:
            self._duty_cycle_tilt = tilt_duty_cycle
        
        if pan_duty_cycle == None or pan_duty_cycle == self._duty_cycle_pan:
            self._duty_cycle_pan = 0
        else:
            self._duty_cycle_pan = pan_duty_cycle
        
        
        self._tilt_servo.ChangeDutyCycle(self._duty_cycle_tilt)        
        self._pan_servo.ChangeDutyCycle(self._duty_cycle_pan)
        time.sleep(0.3)
        if self._duty_cycle_pan != 0:
            self._pan_servo.ChangeDutyCycle(0)
        if self._duty_cycle_tilt != 0:
            self._tilt_servo.ChangeDutyCycle(0)
        time.sleep(0.7)

    def down(self):    
        if self._duty_cycle_tilt <= 7:
            print("Reached down limit")
        else:
            self._duty_cycle_tilt -= 0.5            
            self._tilt_servo.ChangeDutyCycle(self._duty_cycle_tilt)
            time.sleep(0.3)
            self._tilt_servo.ChangeDutyCycle(0)
            time.sleep(0.7)

    def up(self):        
        if self._duty_cycle_tilt >= 11:
            print("Reached up limit")
        else:
            self._duty_cycle_tilt += 0.5        
            self._tilt_servo.ChangeDutyCycle(self._duty_cycle_tilt)
            time.sleep(0.3)
            self._tilt_servo.ChangeDutyCycle(0)
            time.sleep(0.7)
    
    def right(self):        
        if self._duty_cycle_pan >= 11:
            print("Reached right limit")
        else:
            self._duty_cycle_pan += 0.5            
            self._pan_servo.ChangeDutyCycle(self._duty_cycle_pan)
            time.sleep(0.3)
            self._pan_servo.ChangeDutyCycle(0)
            time.sleep(0.7)

    def left(self):        
        if self._duty_cycle_pan <= 2:
            print("Reached left limit")
        else:
            self._duty_cycle_pan -= 0.5            
            self._pan_servo.ChangeDutyCycle(self._duty_cycle_pan)
            time.sleep(0.3)
            self._pan_servo.ChangeDutyCycle(0)
            time.sleep(0.7)

    def stop_camera(self):
        # Stop camera
        #self._camera.stop_preview()

        # Stop servos
        self._tilt_servo.stop()
        self._pan_servo.stop()
        GPIO.cleanup()    
