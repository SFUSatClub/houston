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

import serial
import queue

serialPort = '/dev/cu.usbserial-A700eYE7'
serial_TxQ = queue.Queue()

# Notes:
#   - can either call root. or app. methods from kv file.
# to make children of a class do stuff, search for the comments with: '#CDS ' - the number is the step
# recycleview example: https://github.com/kivy/kivy/blob/master/examples/widgets/recycleview/basic_data.py



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

    def sort(self):
        self.rv.data = sorted(self.rv.data, key=lambda x: x['value'])

    def clear(self):
        self.rv.data = []

    def insert(self, value):
        self.rv.data.insert(0, {'value': value or 'default value'})

    def insert_end(self, value):
        self.rv.data.append({'value': value or 'default value'})

    def update(self, value):
        if self.rv.data:
            self.rv.data[0]['value'] = value or 'default new value'
            self.rv.refresh_from_data()

    def remove(self):
        if self.rv.data:
            self.rv.data.pop(0)

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
        self.rv.data = [{'cmd': 'hello', 'timeout':str(234), 'expect': 'sdf' },
                        {'cmd': 'bye', 'timeout':str(345), 'expect': 'dfv' }] 
                            
        print (self.rv.data)#


    def populate(self):
        self.rv.data = [{'value': ''.join(sample(ascii_lowercase, 6))}
                        for x in range(50)]

    def add_to_sched(self):
        print(self.cmd_entry.text + self.cmd_expected_entry.text + self.cmd_timeout_entry.text)
        
    def sort(self):
        self.rv.data = sorted(self.rv.data, key=lambda x: x['value'])

    def clear(self):
        self.rv.data = []

    def insert(self, value):
        self.rv.data.insert(0, {'value': value or 'default value'})

    def update(self, value):
        if self.rv.data:
            self.rv.data[0]['value'] = value or 'default new value'
            self.rv.refresh_from_data()

    def remove(self):
        if self.rv.data:
            self.rv.data.pop(0)


items = [0, "apple", "dog", 1, "banana", "cat", 2, "pear", "rat", 3,  "pineapple", "bat"]


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

if __name__ == '__main__':
    HoustonApp().run()
