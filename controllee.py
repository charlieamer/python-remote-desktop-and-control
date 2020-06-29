from protocol_base import ProtocolBase
from twisted.internet import reactor
from mss import mss
import io
import PIL
import json
from constants import *
import commands

class ControlleeProtocol(ProtocolBase):
    def __init__(self):
        ProtocolBase.__init__(self)
        print("Controllee init")
        self.config = {}

        self.setVariable(VAR_SCALE, VAR_SCALE_DEFAULT, False)
        self.setVariable(VAR_MONITOR, VAR_MONITOR_DEFAULT, False)
        self.setVariable(VAR_SHOULD_UPDATE_COMMANDS, VAR_SHOULD_UPDATE_COMMANDS_DEFAULT, False)
        self.printConfig()

        reactor.callLater(1, self.sendScreenshot)
        self.commands = commands.Commands(self.config)
        self.commands.start()

    def messageReceived(self, data: bytes):
        decoded = data.decode('ascii')
        if decoded == COMMAND_SEND_SCREENSHOT:
            self.sendScreenshot()
        if decoded.startswith(COMMAND_SET_VAR):
            commandInfo = json.loads(decoded[len(COMMAND_SET_VAR):])
            self.setVariable(**commandInfo)
        if decoded.startswith(COMMAND_NEW_COMMAND):
            commandInfo = json.loads(decoded[len(COMMAND_NEW_COMMAND):])
            self.commands.addCommand(*commandInfo)

    def setVariable(self, variable, value, shouldPrint = True):
        self.config[variable] = value
        if shouldPrint:
            self.printConfig()

    def printConfig(self):
        print(self.config)

    def sendScreenshot(self):
        with io.BytesIO() as output:
            with mss() as sct:
                monitorRequest = self.config[VAR_MONITOR]
                monitorRequest = min(len(sct.monitors) - 1, monitorRequest)
                ss = sct.grab(sct.monitors[monitorRequest])
                ss = PIL.Image.frombytes('RGB', ss.size, ss.bgra, 'raw', 'BGRX')
                if self.config[VAR_SCALE] < 1:
                    ss = ss.resize((int(ss.size[0] * self.config[VAR_SCALE]),
                                    int(ss.size[1] * self.config[VAR_SCALE])))
                ss.save(output, format="JPEG", quality=60)
                self.writeMessage(output.getvalue())
    
    def connectionLost(self, reason):
        self.commands.shouldRun = False
