from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
import copy
from houston_utils import *
import serial
import queue
import pickle
from SatTest import *
from functools import partial
from Command import *
from FileParse import create_dump_command

# Pass in arg to say_hello
# Inherit button class in subdropdown

main_cmds = ['file', 'state', 'deploy', 'wd', 'ack', 'sched', 'task', 'get', 'help', 'help', 'exec', 'rf']
sub_cmds = {'file':['dump','cdump','cprefix','size'],'state':['set','get','prev'],'wd':['reset'],'ack':['default'],'sched':['this is complicated'],'task':['ermm'],'get':['tasks','runtime','heap','minheap','types','epoch'],'help':['errmmm'],'exec':['rf'],'rf':['uhh']}

def test_fun(cmd_drop_down, x):
    setattr(cmd_drop_down, 'text', x)
    sub_dropdown = SubDropDown(cmd_name=x)

class SubDropDown(Button):
    def __init__(self,**kwargs):
        cmd_name = kwargs.pop('cmd_name',None)
        test1 = copy.deepcopy(cmd_name)
        super(SubDropDown,self).__init__(**kwargs)
        self.drop_list = None
        self.drop_list = DropDown()
        if self.drop_list is None:
            print("self drop is none")
        print("sub drop down",test1)
        if (test1 is None) or (test1 not in sub_cmds):
            return
        for i in sub_cmds[test1]:
            print("\n",i)
            sub_btn = Button(text=i, size_hint_y=None, height=50)
            sub_btn.bind(on_release=lambda sub_btn: self.drop_list.select(sub_btn.text))
            self.drop_list.add_widget(sub_btn)
        
        #self.bind(on_release=self.drop_list.open)
        self.bind(on_release=lambda instance : print("Test 2 "))
        #self.drop_list.bind(on_select=lambda instance, x: setattr(self, 'text', x))
        self.drop_list.bind(on_select=lambda instance, x: print("sub cmd test",x))
        
# Creating 3 seprate classes because of kivy bug
# from stack overflow https://stackoverflow.com/questions/21294152/how-to-use-drop-down-widget-in-kivy-with-a-python-class
class CmdDropDown(Button):
    def __init__(self,**kwargs):
        super(CmdDropDown,self).__init__(**kwargs)
        self.drop_list = None
        self.drop_list = DropDown()
        for i in main_cmds:
            btn = Button(text=i, size_hint_y=None, height=50)
            btn.bind(on_release=lambda btn: self.drop_list.select(btn.text))
            self.drop_list.add_widget(btn)
        self.bind(on_release=self.drop_list.open)
        self.drop_list.bind(on_select=lambda instance, x: test_fun(self, x))

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

        # DEBUG
        #cmd_dropdown = CmdDropDown() 
        #test1 = SubDropDown()
        test1 = SubDropDown(cmd_name='file')

        self.serial_TxQ = serial_TxQ
        self.test = test
        cmd0 = Command(0, 'ack', 0, 3, 'Ack!', True) # make a couple default commands
        # cmd0 = Command(0, 'state get', 3, 1, 'SAFE', True) # make a couple default commands
        cmd1 = Command(1, 'ack', 5, 5, 'Ack!', True)
        self.cmds_list = [cmd0, cmd1]
        self.sched_rv.data = list(map(lambda cmd:cmd.cmd_dict(),self.cmds_list)) # https://stackoverflow.com/questions/2682012/how-to-call-same-method-for-a-list-of-objects
        self.cmdid = 2 # unique command ID

    def add_to_sched(self):
        # TODO: bring in the relative time argument from the check box
        # Check for None types
        cmd_entry = self.cmd_entry.text + ' '
        # TODO: If cmd entry  is none, handle this
        # TODO: Handle empty strings
        sub_cmd_entry = self.sub_cmd_entry.text + ' '
        cmd_args = self.cmd_args.text
        cmd_text = cmd_entry+ sub_cmd_entry + cmd_args
        cmd = Command(self.cmdid, cmd_text, self.cmd_epoch_entry.text, self.cmd_timeout_entry.text, self.cmd_expected_entry.text, True)
        print('Schedule: ', cmd.cmdid, cmd.cmd, cmd.expect)
        cmd = self.parse_command(cmd) # format certain commands
        self.sched_rv.data.append(cmd.cmd_dict())
        self.cmds_list.append(cmd)
        self.cmdid += 1

    def clear_sched(self):
        del self.sched_rv.data[:]
        self.cmdid = 0

    def rm_button_press(self, cmdid):
        """ remove command from the list by ID"""
        i = index_of_cmdid(self.cmds_list, cmdid)
        del self.sched_rv.data[i]
        del self.cmds_list[i]
        self.clear_sched()

        startingID = 0                    # zero indexed
        idCounter = startingID

        for cmds in self.cmds_list:     # repopulate schedule tab w/ updated cmds_list and their new id
            cmds.cmdid = idCounter        # keep id count consistent
            self.sched_rv.data.append(cmds.cmd_dict())
            idCounter = idCounter + 1

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


    def parse_command(self, command):
        """ Certain commands require parsing/modification, such as file dump commands.
                - for dump commands, file names are to be sent as hex, so we figure that out here """
        
        if string_find(command.cmd, 'file dump') or string_find(command.cmd, 'file cdump'):
            command.cmd = create_dump_command(command.cmd)

        return command

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
        filename[0] = filename[0].replace('/schedules','',1)  # tends to include the schedules directory twice for some reason
        with open(filename[0], "rb") as handle:
            self.cmds_list_load = pickle.load(handle)

        maxIDNum = self.cmds_list.__len__() - 1     # zero indexed

        for cmds in self.cmds_list_load:
            cmds.cmdid = maxIDNum + 1        # keep id count consistent
            idnum = cmds.cmdid
            self.sched_rv.data.append(cmds.cmd_dict())
            self.cmds_list.append(cmds)
            maxIDNum = maxIDNum + 1         # another command added so ID increment by 1

        self.dismiss_popup()

    def save(self, path, filename):
        if '.pkl' not in filename:
            pickle_File = '{}.pkl'.format(filename) # place pickle file extension on to user input
        else:
            pickle_File = filename
        with open(os.path.join(path, pickle_File), "wb") as handle:
            pickle.dump(self.cmds_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
        self.dismiss_popup()





