from protocol_base import ProtocolBase
import tkinter
from twisted.internet import tksupport, reactor
import hashlib
from PIL import ImageTk, Image
from io import BytesIO
from constants import *
import json
import time

class FactoryControllerBase:
    def __init__(self):
        self.tk = tkinter.Tk()
        tksupport.install(self.tk)

    def buildProtocol(self, addr):
        return ControllerProtocol(self.tk)


class ControllerProtocol(ProtocolBase):
    def __init__(self, tk):
        ProtocolBase.__init__(self)

        print("Controller init")
        self.root = tkinter.Toplevel(tk)
        self.root.state('zoomed')
        self.root.protocol("WM_DELETE_WINDOW", self.onCloseClicked)
        self.lastReceivedTime = time.time()

        frame = tkinter.Frame(self.root)
        frame.pack()

        tkinter.Label(frame, text='Monitor:').pack(side=tkinter.LEFT)
        monScale = tkinter.Scale(frame, from_=0, to=4, orient=tkinter.HORIZONTAL, command=self.changeMonitor)
        monScale.pack(side=tkinter.LEFT)
        monScale.set(VAR_MONITOR_DEFAULT)

        tkinter.Label(frame, text='Scale:').pack(side=tkinter.LEFT)
        scaleScale = tkinter.Scale(frame, from_=0.1, to=1, orient=tkinter.HORIZONTAL, resolution=0.1, command=self.changeScale)
        scaleScale.pack(side=tkinter.LEFT)
        scaleScale.set(VAR_SCALE_DEFAULT)

        self.updateVar = tkinter.BooleanVar(self.root, VAR_SHOULD_UPDATE_COMMANDS_DEFAULT)
        updateCheck = tkinter.Checkbutton(frame, text='Update commands', command=self.changeUpdateCommands, variable=self.updateVar)
        updateCheck.pack(side=tkinter.LEFT)

        tkinter.Label(frame, text='FPS:').pack(side=tkinter.LEFT)
        self.fpsLabel = tkinter.Label(frame, text='?')
        self.fpsLabel.pack(side=tkinter.LEFT)

        self.label = tkinter.Label(self.root)
        self.label.pack(fill=tkinter.BOTH, expand=True)
        # self.label.bind('<Motion>', self.onMouseMoved)
        self.root.bind('<Key>', self.onKeyDown)
        self.root.bind('<KeyRelease>', self.onKeyUp)
        self.label.bind('<Button>', self.onMouseDown)
        self.label.bind('<ButtonRelease>', self.onMouseUp)
    
    def changeScale(self, newScale: str):
        self.setValue(VAR_SCALE, float(newScale))
    
    def changeMonitor(self, newMonitor: str):
        self.setValue(VAR_MONITOR, int(newMonitor))
    
    def changeUpdateCommands(self):
        self.setValue(VAR_SHOULD_UPDATE_COMMANDS, self.updateVar.get())
    
    def setValue(self, variable, value):
        toSend = COMMAND_SET_VAR.encode('ascii')
        toSend += json.dumps({
            'variable': variable,
            'value': value
        }).encode('ascii')
        self.writeMessage(toSend)
    
    def sendCommand(self, commandName, *args):
        toSend = COMMAND_NEW_COMMAND.encode('ascii')
        toSend += json.dumps([commandName, *args]).encode('ascii')
        self.writeMessage(toSend)

    def getLocalPosition(self, x, y):
        labelSize = self.getLabelSize()
        return (x / labelSize[0], y / labelSize[1])

    def onMouseMoved(self, event):
        print(event.x, event.y)
    
    def sendMouseEvent(self, event, isDown: bool):
        location = self.getLocalPosition(event.x, event.y)
        self.sendCommand('MoveMouse', location[0], location[1])
        self.sendCommand('MouseInput', event.num == 1, isDown)

    def onMouseDown(self, event):
        self.sendMouseEvent(event, True)

    def onMouseUp(self, event):
        self.sendMouseEvent(event, False)
    
    def sendKeyEvent(self, event, isDown: bool):
        self.sendCommand('KeyboardInput', event.keycode, isDown)
    
    def onKeyDown(self, event):
        self.sendKeyEvent(event, True)
    
    def onKeyUp(self, event=None):
        self.sendKeyEvent(event, False)

    def onCloseClicked(self):
        self.transport.abortConnection()
        reactor.stop()

    def getLabelSize(self):
        return (self.label.winfo_width(), self.label.winfo_height())

    def messageReceived(self, data: bytes):
        shouldAskMore = False
        newSize = self.getLabelSize()
        img = Image.open(BytesIO(data))
        oldSize = img.size
        img = img.resize(newSize)
        self.currentImage = ImageTk.PhotoImage(img)
        self.label.configure(image=self.currentImage)
        self.fpsLabel['text'] = '%.1f' % (1/(time.time() - self.lastReceivedTime))
        self.lastReceivedTime = time.time()
        self.writeMessage(COMMAND_SEND_SCREENSHOT.encode('ascii'))

    def connectionLost(self, reason):
        print('Connection lost', reason)
        ProtocolBase.connectionLost(self)
        if self.root is not None:
            self.root.destroy()
            self.root = None