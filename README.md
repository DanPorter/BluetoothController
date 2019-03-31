# BluetoothController
A simple Bluetooth controller using Serial commands with a Tkinter graphical user interface

## To run:
```
python BluetoothController.py 
```

 - A window should appear, set the port and baud rate, then press "Connect"
 - Use the joystick to move your T-Bot, or arrow keys (focus must be on the joystick)

## Requirements:
pySerial, Tkinter

if required:
    pip install pySerial
    -or- 
    conda install pySerial (tested in python 2.7 and 3.7)

## Typical port names:
### Windows:
        COM4, COM5, ...
### Linux: 
        

## Typical Baud rates:
    38400

## Notes:
 - Ensure you have paired your bluetooth device with your PC first
 - Select the correct port, in Windows, determine this from the Device Properties screen.
 - Bluetooth via serial can be quite flakey, sometimes you just can't see the device and I'm not sure why yet!
 - There is a standard read and write timeout of 0.1s, which can be changed in the code, if the timeout is triggered, the connection is stopped.
 - Tested and works on Python 2.7 + 3.6 on Windows 10


Version 1.0     31/March/2019

By Dan Porter
2019
