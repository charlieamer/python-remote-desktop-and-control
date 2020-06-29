from transport import get_transport
from twisted.internet import reactor
import argparse
import sys

parser = argparse.ArgumentParser(description='Starts a control session. You can choose to be controlled, or to control someone, and you need to specify who is server and who is client')
parser.add_argument('mode', choices=['controller', 'controllee'], help='Controller: You are the one who controls other computer. Controllee: You are the one being controlled')
parser.add_argument('--host', help='Enter hostname here (or ip address). If you specify this then this means that you are client (you will initiate tcp connection as client). If not specified, you will host a server')
parser.add_argument('--port', type=int, default=5005, help='Which port to use when connecting/starting the server. Default is 5005')
parsed = parser.parse_args()

controller = parsed.mode == 'controller'

if len(sys.argv) < 3:
    sys.argv.append(None)

factory = get_transport(parsed.host, controller, parsed.port)
print("Starting", factory)
reactor.run()