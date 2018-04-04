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

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from houston_utils import *
import serial
import queue

serialPort = '/dev/cu.usbserial-A700eYE7'
serial_TxQ = queue.Queue()

# Notes:
#   - can either call root. or app. methods from kv file.
# to make children of a class do stuff, search for the comments with: '#CDS ' - the number is the step
# recycleview example: https://github.com/kivy/kivy/blob/master/examples/widgets/recycleview/basic_data.py
# thread example: https://github.com/kivy/kivy/wiki/Working-with-Python-threads-inside-a-Kivy-application
# loader example: https://kivy.org/docs/api-kivy.uix.filechooser.html


class MainTab(BoxLayout):
    label_wid = ObjectProperty()
    rv = ObjectProperty()
    txt_entry = ObjectProperty() # text input box

    def send_button_press(self, *args):
        print('Sending_button:' + self.txt_entry.text)
        serial_TxQ.put(self.txt_entry.text)

    def on_enter(self, *args): # gets text from the input box on enter
        thing = args[0]
        print('Sending_enter:' + thing.text)
        serial_TxQ.put(thing.text)


    #rv_handle = ObjectProperty() #CDS 3 - assign objectproperty to the handle

    # def rv_do_sthng(self):
    #     # self.rv_handle.rv_foo("rv hello") #CDS 4 - use the object handle to call methods of that class
    #     self.rv_handle.insert("sdfkjh")
    #
    # def rv_init(self):
    #     self.rv_handle.populate()

    def populate(self):
        self.rv.data = [{'value': 'init'}]

    def insert_end(self, value):
        self.rv.data.append({'value': value or 'default value'})

    def update(self, value):
        if self.rv.data:
            self.rv.data[0]['value'] = value or 'default new value'
            self.rv.refresh_from_data()

class TPI1(TabbedPanelItem):
    def __init__(self):
        TabbedPanelItem.__init__(self)
        self.mt1 = MainTab()
        self.add_widget(self.mt1)

items = [0, "apple", "dog", 1, "banana", "cat", 2, "pear", "rat", 3,  "pineapple", "bat"]

class CMDQTab(TabbedPanelItem):
    def __init__(self):
        TabbedPanelItem.__init__(self)
        self.cmds_list = []
        self.rv.data = [{'cmdid': str(0), 'cmd': 'hello', 'timeout':str(234), 'expect': 'sdf' },
                        {'cmdid': str(1), 'cmd': 'bye', 'timeout':str(345), 'expect': 'dfv' }] 
        self.cmdid = 2 # unique command ID
                            
    def add_to_sched(self):
        print(self.cmd_entry.text + self.cmd_expected_entry.text + self.cmd_timeout_entry.text)
        #TODO: make sure data is ok before adding it
        self.rv.data.append({'cmdid':str(self.cmdid), 'cmd': self.cmd_entry.text, 'timeout':self.cmd_timeout_entry.text, 'expect': self.cmd_expected_entry.text})
        self.cmdid += 1

    def clear_sched(self):
        self.rv.data = []
        self.cmdid = 0;

    def rm_button_press(self, cmdid):
        for i, dic in enumerate(self.rv.data):
            if dic['cmdid'] == cmdid:
                break

        del self.rv.data[i]

    def insert(self, value):
        self.rv.data.insert(0, {'value': value or 'default value'})

    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

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

class Top(TabbedPanel): # top of the visual hierarchy, builds the tabbed panels
    def __init__(self):
        self.stop = threading.Event()
        TabbedPanel.__init__(self)

# Create tabbed panel item instances so we can reference their children
        self.tpi1 = TPI1()
        self.add_widget(self.tpi1)

        self.cmd_q_tab = CMDQTab()
        self.add_widget(self.cmd_q_tab)

        self.tpi1.mt1.populate()

        self.start_second_thread("dfjh")

    def start_second_thread(self, l_text):
        threading.Thread(target=self.second_thread, args=(l_text,)).start()

    def second_thread(self, label_text):
         while True:
            if self.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                # close the log
                return

            self.read_serial()


    def read_serial(self):
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
                else:
                    ser.Close()

        except Exception as error:
            if not self.stop.is_set():
                print(error)
                time.sleep(0.5)
                print('Waiting for serial...')
                # log.write('Waiting for serial: ' + str(time.time()) + '\r\n')
                self.read_serial()

    @mainthread
    def update_label_text(self, new_text):
        # self.tpi1.mt1.ids.lab_2.text = new_text #going down through the hierarchy to access a property
        # self.tpi2.ids.lb1.text = new_text # a top level ish label

        # self.tpi1.mt1.rv_do_sthng() #CDS 6 - going down in the hierarchy a little, call the method that pokes down into the child object's methods
        self.tpi1.mt1.insert_end(new_text)
    pass



class HoustonApp(App): # the top level app class
    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        self.root.stop.set()
        print("Stopping.")

    def build(self):
        self.top = Top()
        return self.top

    def rm_button_press(self, cmdid): #TODO: is it really required to go up to the app like this?
        self.top.cmd_q_tab.rm_button_press(cmdid)

Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    HoustonApp().run()
