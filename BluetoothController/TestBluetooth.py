"""
Test script for playing with Bluetooth code:

$ ipython -i TestBluetooth.py
>> line=bluetooth.readline()


Control Panel>Hardware>Printers>Other Devices>MaximusRoboticus
Bluetooth>Unique identifier
98:d3:32:21:40:d1
Services: Serial Port
COM5

Baud rate
38400

Windows 10 Bluetooth Serial Terminal (Microsoft App store)
https://www.microsoft.com/en-gb/p/bluetooth-serial-terminal/9wzdncrdfst8?activetab=pivot%3Aoverviewtab
"""



import serial
import numpy as np
import matplotlib.pyplot as plt
import time

port = 'COM5' # Device>Services>Serial Port
baud = 38400 # Get from TBot.ino
bluetooth = serial.Serial(port,baud, timeout=0.1, write_timeout=0.1)
time1 = time.time()
print('I am connected!')

#print('write')
#bluetooth.write(b'BOOP'+str.encode(str(5)))
#print('read')
#data = bluetooth.readline().decode()

print('Reading bluetooth buffer:')
line=bluetooth.readline().decode()
time2 = time.time()
#print(line)
print('Time = %6.2f s'%(time2-time1))
print('Line len = %d'%(len(line)))
items=[val.split(',') for val in line.strip('\x02\x03').split('\x03\x02')]
print('Items = %d'%(len(items)))
print('items/s = %6.2f'%(len(items)/(time2-time1)))
if len(items[0]) != len(items[-1]):
	items = np.array(items[1:])
else:
	items = np.array(items)
print('Data accepted!')
"""
plt.figure()
plt.plot(items)
plt.title('T=%6.2f s %d items %d line'%(time2-time1, len(items), len(line)))
plt.legend()
plt.show()
"""
