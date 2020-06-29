# Python remote desktop and control (PRDAC)
![screenshot](https://github.com/charlieamer/python-remote-desktop-and-control/blob/master/images/ss.png?raw=true)


This is my own python version of a software similar to "TeamViewer", "Ammyy Admin", "AnyDesk", etc. This software allows you to controll other computer via network. Such software can be used to work over distance, help others with technical difficulties remotely, etc. We are not responsible for any damage this software has done to any computer. Use it at your own risk.

# Overview
This software connects directly to the same software on another computer via TCP (which means, in some cases you'll have to set-up port forwarding. Default port is 5005). Both controller and the one being controlled can be both server and client (not at the same time though). As a controller, you can send keyboard and mouse input to controllee. Controller can also choose some parameters of session such as which monitor is streamed (all monitors can be streamed at the same time as well), stream quality, etc.

# Dependencies
`pip install twisted mss pillow pynput`

# Usage
One person must be controller, the other person must be controllee (being controlled). One of those persons must be server, the other one must be client.
```
usage: cli.py [-h] [--host HOST] [--port PORT] {controller,controllee}

Starts a control session. You can choose to be controlled, or to control someone, and you need to specify who is server and who is client

positional arguments:
  {controller,controllee}
                        Controller: You are the one who controls other computer. Controllee: You are the one being controlled

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Enter hostname here (or ip address). If you specify this then this means that you are client (you will initiate tcp connection as client). If not specified, you will host a server
  --port PORT           Which port to use when connecting/starting the server. Default is 5005
```

# Known issues
* Platforms other then windows are not tested. In theory this should work.
* You don't see mouse in controllee's mouse. You should just blindly trust that it is there.
* In case of multiple montior setup, a mouse can stop between the monitors when moving. If that happens controllee must either move the mouse manually a bit, or restart the software.
