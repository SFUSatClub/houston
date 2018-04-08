from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty

from houston_utils import *
import serial
import queue
from SatTest import *
from functools import partial

class SCHEDTab(TabbedPanelItem):
    sched_rv = ObjectProperty(None)
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(SCHEDTab, self).__init__(**kwargs)
        # can't call something like initialize() here, needs to be done after build phase

    def initialize(self, serial_TxQ, test):
        # called from Top() since it can't be called from init apparently
        print ("INITIALIZE")
        self.serial_TxQ = serial_TxQ
        self.test = test
        self.cmds_list = []
        self.sched_rv.data = [{'cmdid': str(0), 'cmd': 'state get', 'epoch': str(3), 'timeout': str(1), 'expect': 'SAFE', 'rel': 'True'},
                        {'cmdid': str(1), 'cmd': 'get heap','epoch': str(5), 'timeout': str(2), 'expect': 'heap: 2342', 'rel': 'True' }] 
        self.cmdid = 2 # unique command ID
        
    def add_to_sched(self):
        print(self.cmd_entry.text + self.cmd_expected_entry.text + self.cmd_timeout_entry.text)
        #TODO: make sure data is ok before adding it
        self.sched_rv.data.append({'cmdid':str(self.cmdid), 'cmd': self.cmd_entry.text, 'epoch': self.cmd_epoch_entry.text,'timeout':self.cmd_timeout_entry.text, 'expect': self.cmd_expected_entry.text})
        self.cmdid += 1

    def clear_sched(self):
        self.sched_rv.data = []
        self.cmdid = 0;

    def rm_button_press(self, cmdid):
        """ remove command from the list by ID"""
        i = val_match_dict_in_list(self.sched_rv.data, 'cmdid', cmdid)
        del self.sched_rv.data[i]

    def insert(self, value):
        self.sched_rv.data.insert(0, {'value': value or 'default value'})

    def uplink_schedule(self):
        """ using the kivy clock, we schedule when to put cmds out on the tx queue
        """
        self.test.zero_epoch()
        self.test.add_schedule(self.sched_rv.data[:]) # add all of our commands

        for command in self.sched_rv.data:
            epoch_to_send = int(command['epoch']) # for relative, just subtract current sat epoch
            cmdid = command['cmdid']
            #TODO: determine schedule time from now based on relative flag
            print("COMMAND: ", str(epoch_to_send), str(cmdid))
            Clock.schedule_once(partial(self.test.uplink, cmdid), epoch_to_send)
            Clock.schedule_once(partial(self.test.command_timeout, cmdid), epoch_to_send + int(command['timeout']))

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            self.text_input.text = stream.read()

        self.dismiss_popup()

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()
