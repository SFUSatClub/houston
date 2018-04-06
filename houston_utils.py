#houston_utils.py
# contains some extraneous things that we don't want cluttering up our main file

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import time
import os


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class CommandSchedule():
    def __init__(self, tx_queue):
        self.new = [] # commands that have not yet been sent out to the OBC
        self.pending = [] # commands waiting on valid response or timeout
        self.acknowledged = [] # commands that have been acknowledged properly
        self.errored = [] # commands that timed out
        self.tx_queue = tx_queue
        self.epoch = time.time

    def uplink(self, cmdid, dt):
        print("CMDID_in", str(cmdid))
        for i, dic in enumerate(self.new):
            if dic['cmdid'] == cmdid:
                break
        command = self.new[i]
        
        # rm from new list, put on pending list
        del self.new[i]
        self.pending.append(command)
        print("NEW:", self.new)
        print("command: ", command, str(i))
        print("SCHEDULED COMMAND SEND: " + str(command['cmd']))
        self.tx_queue.put(str(command['cmd']))
        return

