from twisted.internet import reactor
from twisted.internet.protocol import Protocol
import struct

NUM_FORMAT = '<Q'

class ProtocolBase(Protocol):
    def __init__(self):
        self.buffer = bytes([])
        self.receiveBuffer = bytes([])
        self.receiveMessageLength = -1
        reactor.callLater(0.05, self.flush)

    def writeMessage(self, newBytes):
        self.buffer += struct.pack(NUM_FORMAT, len(newBytes))
        self.buffer += newBytes

    def flush(self):
        if len(self.buffer) > 0:
            self.transport.write(self.buffer[:65000])
            self.buffer = self.buffer[65000:]
        reactor.callLater(0.05, self.flush)

    def dataReceived(self, data: bytes):
        self.receiveBuffer += data
        self.processMessage()

    def processMessage(self):
        if self.receiveMessageLength == -1:
            size = struct.calcsize(NUM_FORMAT)
            if len(self.receiveBuffer) < size:
                return
            self.receiveMessageLength = struct.unpack(NUM_FORMAT, self.receiveBuffer[:size])[0]
            self.receiveBuffer = self.receiveBuffer[size:]
            self.processMessage()
        else:
            if self.receiveMessageLength <= len(self.receiveBuffer):
                bufferCopy = self.receiveBuffer[:self.receiveMessageLength]
                self.receiveBuffer = self.receiveBuffer[self.receiveMessageLength:]
                self.receiveMessageLength = -1
                self.messageReceived(bufferCopy)
                self.processMessage()

    def messageReceived(self, message: bytes):
        pass