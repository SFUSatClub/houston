'''
SFUSat Houston
============
Author: Richard Arthurs
April 2018

Ground control app for CubeSat.
'''

import threading
from random import sample
from string import ascii_lowercase
import time
import random
from functools import partial


from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty

from houston_utils import *
import serial
import queue

serialPort = '/dev/cu.usbserial-A700eYE7'
serial_TxQ = queue.Queue()
test = SatTest(serial_TxQ)

# Notes:
#   - can either call root. or app. methods from kv file.
# to make children of a class do stuff, search for the comments with: '#CDS ' - the number is the step
# recycleview example: https://github.com/kivy/kivy/blob/master/examples/widgets/recycleview/basic_data.py
# thread example: https://github.com/kivy/kivy/wiki/Working-with-Python-threads-inside-a-Kivy-application
# loader example: https://kivy.org/docs/api-kivy.uix.filechooser.html
# useful:   https://stackoverflow.com/questions/46284504/kivy-getting-black-screen
#           https://github.com/kivy/kivy/wiki/Snippets

class UARTTab(TabbedPanelItem):
    rv = ObjectProperty()
    uart_entry = ObjectProperty() # text input box

    def __init__(self, **kwargs):
        super(UARTTab, self).__init__(**kwargs)

    def send_button_press(self, *args):
        print('Sending_button:' + self.uart_entry.text)
        serial_TxQ.put(self.uart_entry.text)

    def on_enter(self, *args): # gets text from the input box on enter
        thing = args[0]
        print('Sending_enter:' + thing.text)
        serial_TxQ.put(thing.text)

    def populate(self):
        self.rv.data = [{'value': 'init'}]

    def insert_end(self, value):
        self.rv.data.append({'value': value})

    def update(self, value):
        if self.rv.data:
            self.rv.data[0]['value'] = value 
            self.rv.refresh_from_data()


# class Cmdrow(BoxLayout):
#     epoch = NumericProperty(None)
#     def __init__(self, **kwargs):
#         super(Cmdrow, self).__init__(**kwargs)

class CMDQTab(TabbedPanelItem):
    sched_rv = ObjectProperty(None)
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(CMDQTab, self).__init__(**kwargs)
        # can't call something like initialize() here, needs to be done after build phase

    def initialize(self):
        # called from Top() since it can't be called from init apparently
        print ("INITIALIZE")
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
        for i, dic in enumerate(self.sched_rv.data):
            if dic['cmdid'] == cmdid:
                break

        del self.sched_rv.data[i]

    def insert(self, value):
        self.sched_rv.data.insert(0, {'value': value or 'default value'})

    def uplink_schedule(self):
        # using the kivy clock, we schedule when to put cmds out on the tx queue
        test.zero_epoch()
        test.add_schedule(self.sched_rv.data[:]) # add all of our commands

        for command in self.sched_rv.data:
            epoch_to_send = int(command['epoch']) # for relative, just subtract current sat epoch
            cmdid = command['cmdid']
            #TODO: determine schedule time from now based on relative flag
            print("COMMAND: ", str(epoch_to_send), str(cmdid))
            Clock.schedule_once(partial(test.uplink, cmdid), epoch_to_send)
            # RA: schedule the command timeout here at time epoch + timeout 

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

class RespTab(TabbedPanelItem):
    resp_rv = ObjectProperty(None)

    # command info is added to here when the commands are uplinked
    # results come in with timestamp


    def __init__(self, **kwargs):
        super(RespTab, self).__init__(**kwargs)

    def update_resp(self):
        self.resp_rv.data.append({'cmdid':str(self.cmdid), 'cmd': self.cmd_entry.text, 'timeout':self.cmd_timeout_entry.text, 'expect': self.cmd_expected_entry.text})


class Top(BoxLayout):
    uart_tab = ObjectProperty(None)
    sched_tab = ObjectProperty(None)
    resp_tab = ObjectProperty(None)
    stop = threading.Event()

    def __init__(self, **kwargs):
        super(Top, self).__init__(**kwargs)
        self.setup_tabs()
    
    def setup_tabs(self):
        # since we can't call functions from the constructor of anything but the root element (top), 
        # basically do constructor things here
        self.sched_tab.initialize()
        self.uart_tab.populate()
        self.start_second_thread("example arg")
  
    def start_second_thread(self, l_text):
        threading.Thread(target=self.second_thread, args=(l_text,)).start()

    def second_thread(self, label_text):
         while True:
            if self.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                #TODO: close the log
                return
            self.do_serial()

    def do_serial(self):
        try:
            with serial.Serial(serialPort, 115200, timeout = 10) as ser:
                offset = time.time()

                while(not self.stop.is_set()):
                    while serial_TxQ.qsize() > 0:
                        ser.write(serial_TxQ.get().encode('utf-8'))
                    else:
                        line = ser.readline()
                        if len(line) > 1: # this catches the weird glitch where I only get out one character
                            print (time.time() - offset,':',line.decode('utf-8'))
                            self.update_label_text(str(line.decode('utf-8')))
                            # app.serial_function(str(line.decode('utf-8')))

                            # add it to the test handler class
                            # adds epoch received and the data
                            # from the commands in the pending list, look that this epoch is not greater than timeout, and that data is reasonable
                            # if so, it's a pass
                            # else, it's an orphan print (which is ok)
                else:
                    ser.Close()

        except Exception as error:
            if not self.stop.is_set():
                print(error)
                time.sleep(0.5)
                print('Waiting for serial...')
                # log.write('Waiting for serial: ' + str(time.time()) + '\r\n')
                self.do_serial()

    @mainthread
    def update_label_text(self, new_text):
        self.uart_tab.insert_end(new_text)
    pass


class HoustonApp(App): # the top level app class
    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.

        # root is a reference to the Top instance, auto populated by Kivy
        self.root.stop.set()
        print("Stopping.")

    def build(self):
        # must immediately return Top() here, cannot do something like self.top = Top, and call other functions
        return Top()

    def rm_button_press(self, cmdid): #TODO: is it really required to go up to the app like this?
        self.root.sched_tab.rm_button_press(cmdid)

    def serial_function(self, data):
        print("Serial fun, " + data)

Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    HoustonApp().run()
