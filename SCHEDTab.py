from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty

from houston_utils import *
import serial
import queue
from SatTest import *
from functools import partial
from Command import *

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
        cmd0 = Command(0, 'state get', 3, 1, 'SAFE', True) # make a couple default commands
        cmd1 = Command(1, 'get heap', 5, 2, '4192 bytes', True)
        self.cmds_list = [cmd0, cmd1]
        self.sched_rv.data = list(map(lambda cmd:cmd.cmd_dict(),self.cmds_list)) # https://stackoverflow.com/questions/2682012/how-to-call-same-method-for-a-list-of-objects 
        self.cmdid = 2 # unique command ID
        
    def add_to_sched(self):
        # TODO: bring in the relative time argument from the check box
        cmd = Command(self.cmdid, self.cmd_entry.text, self.cmd_epoch_entry.text, self.cmd_timeout_entry.text, self.cmd_expected_entry.text, True)
        print('Schedule: ', cmd.cmdid, cmd.cmd, cmd.expect)
        self.sched_rv.data.append(cmd.cmd_dict())
        self.cmds_list.append(cmd)
        self.cmdid += 1

    def clear_sched(self):
        self.sched_rv.data = []
        self.cmdid = 0;

    def rm_button_press(self, cmdid):
        """ remove command from the list by ID"""
        i = index_of_cmdid(self.cmds_list, cmdid)
        del self.sched_rv.data[i]
        del self.cmds_list[i]


    def uplink_schedule(self):
        """ using the kivy clock, we schedule when to put cmds out on the tx queue
        """
        self.test.zero_epoch() #TODO: we won't always do this - use real sat epoch
        self.test.add_schedule(self.cmds_list[:]) # add all of our commands

        for cmd in self.cmds_list:
            epoch_to_send = cmd.epoch # for relative, just subtract current sat epoch .. that's why we have a var 
            #TODO: determine schedule time from now based on relative flag
            
            print("COMMAND: ", epoch_to_send, cmd.cmdid)
            Clock.schedule_once(partial(self.test.uplink, cmd.cmdid), int(epoch_to_send))
            Clock.schedule_once(partial(self.test.command_timeout, cmd.cmdid), epoch_to_send + cmd.timeout)

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



