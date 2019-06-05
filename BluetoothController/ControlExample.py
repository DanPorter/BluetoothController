#import pygame, sys, pygame.mixer
#from pygame.locals import *
import serial
from time import sleep


port = 'COM5' # Device>Services>Serial Port
baud = 38400 # Get from TBot.ino
bluetooth = serial.Serial(port,baud)

def send(sendstr):
    try:
        sock.write(sendstr.encode(encoding='utf-8'))
    except:
        bluetooth.close()
        sys.exit()

for jx in range(150,280,10)+[200]:
        jy = jx
        print('x '+str(jx)+' y '+str(jy))
        sendstring = chr(0X02)+str(jx)+str(jy)+chr(0X03)
        send(sendstring)
        sleep(2)

bluetooth.close()
sys.exit()