"""
Bluetooth controller for T-Bot, using Tkinter
To run:
python Dan_Bluetooth_GUI.py 
 >> window should appear, set the port and baud rate, then press "Connect"
 >> Use the joystick to move your T-Bot, or arrow keys (focus must be on the joystick)

Requirements:
pySerial, Tkinter

if required:
    pip install pySerial
    -or- 
    conda install pySerial (tested in python 2.7 and 3.7)

Typical port names:
    Windows:
        COM4, COM5, ...
    Linux: 

Typical Baud rates:
    38400

Version 1.0     03/Feb/2019

By Dan Porter
2019
"""

import math
try:
    import Tkinter as tk # python 3+
except ImportError:
    import tkinter as tk # python 2
import serial # pip install pySerial
from serial.tools import list_ports


#####################################################################
#######################  Interface Functions  #######################
#####################################################################

# Fonts
TF= ["Times", 20, 'bold'] # title font
BF= ["Times", 14] # button font
SF= ["Times New Roman", 14] # Small font
LF= ["Times", 14, 'bold'] # large font
HF= ['Courier',12] # 
# Colours - background
bkg = 'snow'
ety = 'white'
btn = 'light slate blue'
opt = 'light slate blue'
# Colours - active
btn_active = 'grey'
opt_active = 'grey'
# Colours - Fonts
txtcol = 'black'
btn_txt = 'black'
ety_txt = 'black'
opt_txt = 'black'


class TbotGui:
    """
    Simple graphical user interface to send commands to the T-Bot

    1. set the port and baud rate, then press "Connect"
    2. Use the joystick to move your T-Bot, 
    3. or arrow keys (focus must be on the joystick)
    4. Press "Listen" to read a single line from the T-Bot
    5. When finished, close the connection using "Disconnect"
    """
    def __init__(self):
        """Initialise"""
        
        self.bluetooth = None
        # Ports
        ports = list_ports.comports()
        portlist = [p.device for p in ports]
        if len(portlist) < 1:
            raise Exception('Bluetooth is not active')

        # Create Tk inter instance
        self.root = tk.Tk()
        self.root.wm_title('T-Bot Controller by D G Porter')
        # self.root.minsize(width=640, height=480)
        self.root.maxsize(width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.root.tk_setPalette(
            background=bkg,
            foreground=txtcol,
            activeBackground=opt_active,
            activeForeground=txtcol)

        self.joybox_size = 100
        self.joystick_size = 60
        self.pixel_x = self.joybox_size//2
        self.pixel_y = self.joybox_size//2
        self.joystick_x = 0.0
        self.joystick_y = 0.0
        
        w = tk.Label(self.root, text='T-Bot Controller', bg='red', font=TF)
        w.pack(expand=tk.YES, fill=tk.X)

        self.notification = tk.StringVar(self.root, 'Not Connected')
        w = tk.Label(self.root, textvariable=self.notification, bg='light blue', font=LF)
        w.pack(expand=tk.YES, fill=tk.X)

        # Line 1
        frame = tk.Frame(self.root)
        frame.pack()

        w = tk.Label(frame, text='Port:', font=SF, width=10)
        w.pack(side=tk.LEFT)

        self.port = tk.StringVar(frame, portlist[0])
        w = tk.Entry(frame, textvariable=self.port, font=SF, width=10, bg=ety, fg=ety_txt)
        w.bind('<Return>',self.startBluetooth)
        w.bind('<KP_Enter>',self.startBluetooth)
        w.pack(side=tk.LEFT)

        self.portname = tk.StringVar(frame, portlist[0])
        w = tk.OptionMenu(frame, self.portname, *portlist, command=self.portOption)
        w.config(font=SF, width=5, bg=opt, activebackground=opt_active)
        w["menu"].config(bg=opt, bd=0, activebackground=opt_active)
        w.pack(side=tk.LEFT)

        w = tk.Button(frame, text='Connect', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.startBluetooth)
        w.pack(side=tk.RIGHT)

        # Line 2
        frame = tk.Frame(self.root)
        frame.pack()

        w = tk.Label(frame, text='Baud rate:', font=SF, width=10)
        w.pack(side=tk.LEFT)

        self.baud = tk.IntVar(frame, 38400)
        w = tk.Entry(frame, textvariable=self.baud, font=SF, width=20, bg=ety, fg=ety_txt)
        w.bind('<Return>',self.startBluetooth)
        w.bind('<KP_Enter>',self.startBluetooth)
        w.pack(side=tk.LEFT)

        w = tk.Button(frame, text='Disconnect', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.stopBluetooth)
        w.pack(side=tk.RIGHT)

        # Line 3
        frame = tk.Frame(self.root)
        frame.pack(expand=tk.YES, fill=tk.X)

        w = tk.Button(frame, text='Write', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.writeLine)
        w.pack(side=tk.LEFT)

        self.write = tk.StringVar(frame, '300200')
        w = tk.Entry(frame, textvariable=self.write, font=SF, width=10, bg=ety, fg=ety_txt)
        w.bind('<Return>',self.writeLine)
        w.bind('<KP_Enter>',self.writeLine)
        w.pack(side=tk.LEFT)

        w = tk.Button(frame, text='Read', width=8, font=BF, bg=btn, fg=btn_txt)
        w.config(command=self.readBluetooth)
        w.pack(side=tk.LEFT)

        w = tk.Button(frame, text='Program', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.program)
        w.pack(side=tk.LEFT)

        # Line 4
        frame = tk.Frame(self.root, bg='black')
        frame.pack(expand=tk.YES, fill=tk.BOTH)

        # Joystick box
        self.joybox = tk.Canvas(frame, 
            bg='white', 
            height=self.joybox_size, 
            width=self.joybox_size)
        self.joybox.bind('<B1-Motion>', self.onLeftDrag) 
        self.joybox.bind('<ButtonPress-1>', self.onLeftClick)
        self.joybox.bind('<ButtonRelease-1>', self.onLeftRelease)
        self.joybox.bind('<Up>', self.onUpPress)
        self.joybox.bind('<Down>', self.onDownPress)
        self.joybox.bind('<Left>', self.onLeftPress)
        self.joybox.bind('<Right>', self.onRightPress)
        #self.joybox.bind('a', self.onUpPress)
        self.joybox.pack(side=tk.LEFT, padx=20, pady=20)
        self.joybox.focus_set()

        # Joystick image
        self.joybox.create_oval(
            self.pixel_x-5, 
            self.pixel_y-5, 
            self.pixel_x+5, 
            self.pixel_y+5, 
            fill='black')
        self.stk = self.joybox.create_line(
            self.pixel_x,
            self.pixel_y,
            self.pixel_x,
            self.pixel_y,
            fill='black', width=10)
        pos = self.circle(
            xpos=self.pixel_x, 
            ypos=self.pixel_y, 
            size=self.joystick_size//2)
        self.joy = self.joybox.create_polygon(pos, fill='slateblue')


        #--- Text box ---
        frame_box = tk.Frame(frame)
        frame_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)
        
        # Scrollbars
        scanx = tk.Scrollbar(frame_box,orient=tk.HORIZONTAL)
        scanx.pack(side=tk.BOTTOM, fill=tk.X)
        
        scany = tk.Scrollbar(frame_box)
        scany.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Editable string box
        self.text = tk.Text(frame_box, width=10, height=5, font=HF)
        self.text.insert(tk.END,'Output will appear here:')
        self.text.config(wrap=tk.NONE, state=tk.DISABLED)
        self.text.pack(side=tk.TOP,fill=tk.BOTH, expand=tk.YES)
        
        self.text.config(xscrollcommand=scanx.set,yscrollcommand=scany.set)
        scanx.config(command=self.text.xview)
        scany.config(command=self.text.yview)

        # Start GUI
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    ###################################################################################
    ############################## FUNCTIONS ##########################################
    ###################################################################################
    def circle(self, xpos=0, ypos=0, size=1.0, flat=1.0, rot=0.0):
        """
        Create coordinates of rotated oval 
        """
        ang_deg = range(361)
        ang_rad = [math.radians(ang) for ang in ang_deg]
        x = [flat*math.sin(ang) for ang in ang_rad]
        y = [math.cos(ang) for ang in ang_rad]
        xx = [x[n]*math.cos(rot)-y[n]*math.sin(rot) for n in ang_deg]
        yy = [x[n]*math.sin(rot)+y[n]*math.cos(rot) for n in ang_deg]
        out = []
        for n in ang_deg:
            out += [xpos+size*xx[n], ypos+size*yy[n]]
        return out

    def writeOutput(self, outstring):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END,'%s\n'%outstring)
        self.text.config(state=tk.DISABLED)
        self.text.see(tk.END)

    def clearOutput(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)

    def portOption(self, event=None):
        portname=self.portname.get()
        self.port.set(portname)

    def program(self):
        ProgramGui(self)

    def writeLine(self, event=None):
        line = self.write.get()
        line = '\x02'+line+'\x03'
        print('%r == %s'%(line,line))
        self.writeBluetooth(line)

    #####################################################################
    #######################  Bluetooth Functions  #######################
    #####################################################################

    def startBluetooth(self, event=None):
        """Connect to Bluetooth Device"""

        if self.bluetooth is not None: 
            self.bluetooth.close()

        self.notification.set('Connecting...')

        portname = self.port.get()
        baudrate = self.baud.get()
        try:
            self.bluetooth = serial.Serial(portname, baudrate, timeout=0.1, write_timeout=0.1)
            self.notification.set('Connected')
        except serial.serialutil.SerialException:
            self.bluetooth = None
            self.notification.set('Can\'t Connect')
            return
            #self.notification.set('Dan_Bluetooth_text.txt Connected')
            #self.bluetooth = open('Dan_Bluetooth_test.txt', 'w+b')
        self.clearOutput()
        # Test connection
        self.writeBluetooth('Connected...')

    def stopBluetooth(self):
        """Disconnect from Bluetooth Device"""
        if self.bluetooth is None: return
        self.bluetooth.close()
        self.notification.set('Disconnected')
        self.bluetooth = None

    def readBluetooth(self):
        """Read current bluetooth buffer as text line"""
        if self.bluetooth is None: return
        #try:
        #line = bluetooth.readline().decode().strip().split()
        line = self.bluetooth.readline().decode().strip()
        if len(line) > 0:
            self.writeOutput(line)
        else:
            self.writeOutput('Empty')
        try:
            pass
        except:
            self.notification.set('Read didn\'t work')
            self.stopBluetooth()
            line = []
        return line

    def output2array(self, line):
        """Read T-Bot Bluetooth output as an array"""
        items = [val.split(',') for val in line.strip('\x02\x03').split('\x03\x02')]
        if len(items[0]) != len(items[-1]):
            items = items[1:]
        return items


    def writeBluetooth(self, sendstr):
        """Write string to bluetooth device"""
        if self.bluetooth is None: return
        try:
            self.bluetooth.write(sendstr.encode('ascii', 'ignore'))
            self.writeOutput(sendstr.encode('ascii', 'ignore'))
            #print('Sent: %s'%sendstr.encode(encoding='utf-8'))
        except:
            self.writeOutput('Write didn\'t work')
            self.stopBluetooth()

    def blueJoystick(self):
        """Create Joystick string"""
        # Convert normalised float joystick values to 
        # integers from 100-300
        jx = int(self.joystick_x*100 + 200)
        jy = int(-self.joystick_y*100 + 200)
        sendstring = chr(0X02)+str(jx)+str(jy)+chr(0X03)
        self.writeBluetooth(sendstring)

    def getJoyStick(self, event):
        w = event.widget
        xpos = event.x
        ypos = event.y
        xmax = w.winfo_width()
        ymax = w.winfo_height()

        xrat = float(xpos)/xmax - 0.5
        yrat = float(ypos)/ymax - 0.5
        dist = (xrat**2 + yrat**2)**0.5
        angle = math.atan2(yrat, xrat)
        if dist > 0.25: dist=0.25
        x = dist*math.cos(angle)
        y = dist*math.sin(angle)

        self.joystick_x = x*4
        self.joystick_y = y*4
        self.pixel_x = int((0.5 + x)*self.joybox_size)
        self.pixel_y = int((0.5 + y)*self.joybox_size)

    def returnJoyStick(self):
        self.pixel_x = self.joybox_size//2
        self.pixel_y = self.joybox_size//2
        self.joystick_x = 0
        self.joystick_y = 0

    def joyStickMove(self):
        joyx = self.joystick_x
        joyy = self.joystick_y
        #print('Joystick: X=%5.2f Y=%5.2f'%(joyx, joyy))

        dist = 1-0.5*(joyx**2 + joyy**2)**0.5
        angle = math.atan2(joyy, joyx)
        pos = self.circle(
            xpos=self.pixel_x, 
            ypos=self.pixel_y, 
            size=self.joystick_size//2, 
            flat=dist, 
            rot=angle)

        self.joybox.coords(self.stk,
            self.joybox_size//2,
            self.joybox_size//2,
            self.pixel_x,
            self.pixel_y)
        self.joybox.coords(self.joy, *pos)

        # Send Bluetooth Command:
        self.blueJoystick()

    def onLeftDrag(self, event):
        self.getJoyStick(event)
        self.joyStickMove()
        
    def onLeftClick(self, event):
        self.joybox.focus_set()
        self.getJoyStick(event)
        self.joyStickMove()

    def onLeftRelease(self, event):
        self.returnJoyStick()
        self.joyStickMove()

    def onUpPress(self, event):
        if self.joystick_y >= -0.5:
            self.joystick_y -= 0.5
            self.pixel_y -= int(0.125*self.joybox_size)
            self.joyStickMove()
        
    def onDownPress(self, event):
        if self.joystick_y <= 0.5:
            self.joystick_y += 0.5
            self.pixel_y += int(0.125*self.joybox_size)
            self.joyStickMove()

    def onLeftPress(self, event):
        if self.joystick_x >= -0.5:
            self.joystick_x -= 0.5
            self.pixel_x -= int(0.125*self.joybox_size)
            self.joyStickMove()

    def onRightPress(self, event):
        if self.joystick_x <= 0.5:
            self.joystick_x += 0.5
            self.pixel_x += int(0.125*self.joybox_size)
            self.joyStickMove()

    def on_closing(self):
        """close window"""
        print('GoodByee!')
        self.root.destroy()
        self.stopBluetooth()


class ProgramGui:
    """
    Programming GUI
    """
    def __init__(self, parent):
        """Initialise"""
        
        self.parent = parent

        # Create Tk inter instance
        self.root = tk.Tk()
        self.root.wm_title('T-Bot Programmer by D G Porter')
        # self.root.minsize(width=640, height=480)
        self.root.maxsize(width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.root.tk_setPalette(
            background=bkg,
            foreground=txtcol,
            activeBackground=opt_active,
            activeForeground=txtcol)

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=tk.YES)

        # ---Command Box---
        fbox = tk.Frame(frame)
        fbox.pack(side=tk.LEFT, fill=tk.Y, expand=tk.YES)
        
        scl_scanx = tk.Scrollbar(fbox,orient=tk.HORIZONTAL)
        scl_scanx.pack(side=tk.BOTTOM, fill=tk.BOTH)
        
        scl_scany = tk.Scrollbar(fbox)
        scl_scany.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        self.lst_scan = tk.Listbox(fbox, font=HF, selectmode=tk.SINGLE, width=30, height=10,
                                xscrollcommand=scl_scanx.set,yscrollcommand=scl_scany.set)
        self.lst_scan.configure(exportselection=False)
        
        # Populate list box
        self.lst_scan.insert(tk.END, '# Add Commands here') 
        
        self.lst_scan.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        self.lst_scan.select_set(0)
        #self.lst_scan.bind("<<ListboxSelect>>", self.f_scan_select)
        #print( self.lst_scan.curselection()[0] )
        
        scl_scanx.config(command=self.lst_scan.xview)
        scl_scany.config(command=self.lst_scan.yview)
        
        #self.txt_scan.config(xscrollcommand=scl_scanx.set,yscrollcommand=scl_scany.set)

        # ---Command Buttons---
        fcmd = tk.Frame(frame)
        fcmd.pack(side=tk.RIGHT, fill=tk.X, expand=tk.YES)

        w = tk.Button(fcmd, text='Forwards', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.but_forwards)
        w.pack()
        w = tk.Button(fcmd, text='Backwards', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.but_backwards)
        w.pack()
        w = tk.Button(fcmd, text='Left', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.but_left)
        w.pack()
        w = tk.Button(fcmd, text='Right', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.but_right)
        w.pack()

        self.write = tk.StringVar(fcmd, '300200')
        w = tk.Entry(fcmd, textvariable=self.write, font=SF, width=10, bg=ety, fg=ety_txt)
        w.bind('<Return>',self.but_write)
        w.bind('<KP_Enter>',self.but_write)
        w.pack()

        w = tk.Button(fcmd, text='Write', width=10, font=BF, bg=btn, fg=btn_txt)
        w.config(command=self.but_write)
        w.pack()

        w = tk.Button(fcmd, text='Speak', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.but_speak)
        w.pack()

        w = tk.Button(fcmd, text='Delete', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.but_delete)
        w.pack()

        w = tk.Button(fcmd, text='RUN', font=BF, width=10, bg=btn, fg=btn_txt)
        w.config(command=self.but_run)
        w.pack()

    ########################## Functions ##############################
    def but_forwards(self):
        self.lst_scan.insert(tk.END, 'FORWARDS')

    def but_backwards(self):
        self.lst_scan.insert(tk.END, 'BACKWARDS')

    def but_left(self):
        self.lst_scan.insert(tk.END, 'LEFT')

    def but_right(self):
        self.lst_scan.insert(tk.END, 'RIGHT')

    def but_write(self, event=None):
        txt = self.write.get()
        self.lst_scan.insert(tk.END, 'WRITE(%s)'%txt)

    def but_speak(self):
        self.lst_scan.insert(tk.END, 'SPEAK')

    def but_delete(self):
        selection = self.lst_scan.curselection()
        for sel in selection:
            self.lst_scan.delete(sel, sel)

    def but_run(self):
        pass

if __name__ == '__main__':
    tbot = TbotGui()