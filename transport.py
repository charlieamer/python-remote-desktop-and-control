from twisted.internet.protocol import *
from twisted.internet.endpoints import *
from twisted.internet import reactor
from controller import ControllerProtocol, FactoryControllerBase
from controllee import ControlleeProtocol

class OurClientFactory(ReconnectingClientFactory):
    maxDelay = 5
    factor = 1
    def buildProtocol(self, addr):
        print("Build protocol called")
        self.resetDelay()
        return ReconnectingClientFactory.buildProtocol(self, addr)

class ControllerFactoryServer(FactoryControllerBase, Factory):
    pass

class ControllerFactoryClient(FactoryControllerBase, OurClientFactory):
    pass

class ControlleeFactoryServer(Factory):
    protocol = ControllerProtocol

class ControlleeFactoryClient(OurClientFactory):
    protocol = ControlleeProtocol

def get_transport(ip: str, isController: bool, port: int):
    if ip is None:
        factory = ControllerFactoryServer() if isController else ControlleeFactoryServer()
        reactor.listenTCP(port, factory)
        return factory
    else:
        factory = ControllerFactoryClient() if isController else ControlleeFactoryClient()
        reactor.connectTCP(ip, port, factory)
        return factory