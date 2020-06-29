from pynput import mouse, keyboard
from constants import *
from mss import mss
import time
import math
from typing import List
import threading

def vector_subract(a, b):
    return (a[0] - b[0], a[1] - b[1])

def vector_length(vec):
    return math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])

def vector_normalize(vec, l = None):
    if l is None:
        l = vector_length(vec)
    if l > 0:
        return (vec[0] / l, vec[1] / l)
    else:
        return (0, 0)

def vector_multiply(vec, m: float):
    return (vec[0] * m, vec[1] * m)

def vector_round(vec):
    return (round(vec[0]), round(vec[1]))

class CommandBase():
    def __init__(self, config: dict):
        self.isDone = False
        self.config = config
        self.frame = -1
        print("Command created", self)

    def start(self):
        self.timeStart = time.time()
        print("Command started", self)

    def update(self):
        self.frame += 1
    
    def time(self):
        return time.time() - self.timeStart

    def finish(self):
        self.isDone = True
        print("Command finished", self)
    
    def __str__(self):
        return self.__class__.__name__

class CommandMoveMouse(CommandBase):
    speed = 10

    def __init__(self, config: dict, x: float, y: float):
        with mss() as sct:
            m = sct.monitors[config[VAR_MONITOR]]
            self.target = (round(m['width'] * x + m['left']),
                           round(m['height'] * y + m['top']))
        CommandBase.__init__(self, config)

    def start(self):
        CommandBase.start(self)
        self.controller = mouse.Controller()

    def update(self):
        CommandBase.update(self)
        
        vecToTarget = vector_subract(self.target, self.controller.position)
        l = vector_length(vecToTarget)
        if l < self.speed:
            self.controller.position = self.target
            self.finish()
        else:
            rel = vector_normalize(vecToTarget, l)
            rel = vector_multiply(rel, self.speed)
            rel = vector_round(rel)
            self.controller.move(rel[0], rel[1])
    
    def __str__(self):
        ret = 'Move mouse ' + str(self.target[0]) + 'x' + str(self.target[1])
        return ret

class CommandMouseInput(CommandBase):
    def __init__(self, config: dict, isLeft: bool, isDown: bool):
        self.isLeft = isLeft
        self.isDown = isDown
        CommandBase.__init__(self, config)
    def update(self):
        CommandBase.update(self)
        if self.frame == 0:
            controller = mouse.Controller()
            btn = mouse.Button.left if self.isLeft else mouse.Button.right
            if self.isDown:
                controller.press(btn)
            else:
                controller.release(btn)
        # if self.time() > 0.0:
        self.finish()
    def __str__(self):
        return ('Left' if self.isLeft else 'Right') + ' mouse ' + \
                ('Down' if self.isDown else 'Up')

class CommandKeyboardInput(CommandBase):
    def __init__(self, config: dict, keycode: int, isDown: bool):
        self.keycode = keycode
        self.isDown = isDown
        CommandBase.__init__(self, config)
    
    def update(self):
        CommandBase.update(self)
        if self.frame == 0:
            controller = keyboard.Controller()
            kc = keyboard.KeyCode(self.keycode)
            if self.isDown:
                controller.press(kc)
            else:
                controller.release(kc)
        # if self.time() > 0.1:
        self.finish()

    def __str__(self):
        return ('Press ' if self.isDown else 'Release ') + str(self.keycode)

class Commands(threading.Thread):
    command_mappings = {
        'MoveMouse': CommandMoveMouse,
        'MouseInput': CommandMouseInput,
        'KeyboardInput': CommandKeyboardInput
    }

    def __init__(self, config, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.currentCommands = [] # type: List[CommandBase]
        self.shouldRun = True
        self.config = config
    
    def addCommand(self, commandName: str, *args):
        instance = self.command_mappings[commandName](self.config, *args)
        self.addCommandInstance(instance)
    
    def addCommandInstance(self, commandInstance):
        self.currentCommands.append(commandInstance)
        if len(self.currentCommands) == 1:
            self.currentCommands[0].start()
    
    def finishCurrentCommand(self):
        if len(self.currentCommands) > 0:
            self.currentCommands = self.currentCommands[1:]
            if len(self.currentCommands) > 0:
                self.currentCommands[0].start()

    def updateCommand(self):
        if len(self.currentCommands) > 0:
            self.currentCommands[0].update()
            if self.currentCommands[0].isDone:
                self.finishCurrentCommand()
    
    def run(self):
        while self.shouldRun:
            if self.config[VAR_SHOULD_UPDATE_COMMANDS]:
                self.updateCommand()
            time.sleep(0.01)