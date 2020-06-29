import tkinter as tk
from tkinter import simpledialog
from transport import get_transport
from twisted.internet import tksupport, reactor

def base_start(isController: bool):
    global isServer

    client_ip = None
    if not isServer.get():
        global root
        client_ip = simpledialog.askstring("Client config", "Enter host", parent=root)
    get_transport(client_ip, isController)

def start_controller():
    base_start(True)

def start_controllee():
    base_start(False)

def window_closed():
    reactor.stop()

if __name__ == "__main__":
    root = tk.Tk()

    isServer = tk.BooleanVar(root)

    controllerButton = tk.Button(root, text="Control somebody", command=start_controller)
    controllerButton.pack(fill=tk.X)
    controlleeButton = tk.Button(root, text="Be controlled", command=start_controllee)
    controlleeButton.pack(fill=tk.X)
    tk.Label(root, text="Network options:").pack(fill=tk.X)
    tk.Radiobutton(root, text="Server", variable=isServer, value=True).pack(fill=tk.X)
    tk.Radiobutton(root, text="Client", variable=isServer, value=False).pack(fill=tk.X)
    
    tksupport.install(root)
    root.protocol("WM_DELETE_WINDOW", window_closed)
    reactor.run()
    