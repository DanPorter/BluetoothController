"""

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

port = 'COM5' # Device>Services>Serial Port
baud = 38400 # Get from TBot.ino
bluetooth = serial.Serial(port,baud)

#print('write')
#bluetooth.write(b'BOOP'+str.encode(str(5)))
#print('read')
#data = bluetooth.readline().decode()

val = 1000
num1 = np.zeros(val)
num2 = np.zeros(val)
num3 = np.zeros(val)
tot1 = np.zeros(val+1)
tot2 = np.zeros(val+1)
tot3 = np.zeros(val+1)
for n in range(val):
	line=bluetooth.readline().decode().strip().split()
	print(line)
	if len(line) != 3: continue
	num1[n] = np.float(line[0])
	num2[n] = np.float(line[1])
	num3[n] = np.float(line[2])
	tot1[n+1] = tot1[n]+np.float(line[0])
	tot2[n+1] = tot2[n]+np.float(line[1])
	tot3[n+1] = tot3[n]+np.float(line[2])

bluetooth.close()

plt.figure()
plt.plot(num1, '-', lw=2, label='vxy')
plt.plot(num2, '-', lw=1, label='spinval')
plt.plot(num3, '-', lw=1, label='rtrim')
plt.legend(loc=0, frameon=False)
plt.show()

plt.figure()
plt.plot(tot1, '-', lw=2, label='vxy')
plt.plot(tot2, '-', lw=1, label='spinval')
plt.plot(tot3, '-', lw=1, label='rtrim')
plt.title('sum')
plt.legend(loc=0, frameon=False)
plt.show()