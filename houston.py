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
from collections import deque

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
from SatTest import *
from UARTTab import *
from RESPTab import *
from SCHEDTab import *

# serialPort = '/dev/cu.usbserial-A700eYE7'
serialPort = '/dev/tty.usbserial-TIXRGQDLB'
serial_TxQ = queue.Queue()
txQ = deque()
test = SatTest(txQ)

# Notes:
#   - can either call root. or app. methods from kv file.
# to make children of a class do stuff, search for the comments with: '#CDS ' - the number is the step
# recycleview example: https://github.com/kivy/kivy/blob/master/examples/widgets/recycleview/basic_data.py
# thread example: https://github.com/kivy/kivy/wiki/Working-with-Python-threads-inside-a-Kivy-application
# loader example: https://kivy.org/docs/api-kivy.uix.filechooser.html
# useful:   https://stackoverflow.com/questions/46284504/kivy-getting-black-screen
#           https://github.com/kivy/kivy/wiki/Snippets


# class Cmdrow(BoxLayout):
#     epoch = NumericProperty(None)
#     def __init__(self, **kwargs):
#         super(Cmdrow, self).__init__(**kwargs)

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
        self.sched_tab.initialize(txQ, test)
        self.uart_tab.populate(txQ)
        self.start_second_thread("example arg")
  
    def start_second_thread(self, l_text):
        print('thread started')
        threading.Thread(target=self.second_thread).start()

    def second_thread(self):
        while not self.stop.is_set():
            self.do_serial()
        else:
            return

    def do_serial(self):
        try:
            # with serial.Serial(serialPort, 115200, timeout = 10) as ser:
            ser = serial.Serial(serialPort, 115200, timeout = 10) 
            self.offset = time.time() # time we start things up

            while(ser.isOpen() and not self.stop.is_set()):
                if ser.inWaiting() > 0:
                    line = ser.readline()  #read the bytes and convert from binary array to ASCII
                    if len(line) > 1: # this catches the weird glitch where I only get out one character
                        self.dispatch_telem(line)
                else:
                    try:
                        cmd = str(txQ.popleft())
                        #  serial_TxQ.qsize() > 0:
                        # print('yuh')
                        # cmd = str(serial_TxQ.get())
                        for char in cmd:
                            ser.write(char.encode('ascii'))
                            time.sleep(0.05)
                            # print('Sent: '+ char)

                        ser.write('\r\n'.encode('ascii'))
                    except IndexError:
                        pass
                
            else:
                ser.Close()

        except Exception as error:
            if not self.stop.is_set():
                print(error)
                time.sleep(0.1)
                print('Waiting for serial...')
                # log.write('Waiting for serial: ' + str(time.time()) + '\r\n')
                self.do_serial()

    def dispatch_telem(self, line):
        """ Here we do several different things with the telemetry that comes in """
        print (time.time() - self.offset,':',line.decode(encoding = 'ascii'))
        self.update_label_text(line.decode(encoding = 'ascii').expandtabs(tabsize=8)) # expand tabs to get rid of unknown tab char that can come in

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
