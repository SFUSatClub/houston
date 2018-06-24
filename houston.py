#!/usr/bin/env python
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

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # Stop red dots from appearing on right click
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
from kivy.uix.settings import SettingsWithSidebar

from houston_utils import *
import serial
import queue
from SatTest import *
from UARTTab import *
from RESPTab import *
from SCHEDTab import *
from FileParse import *
from DASHTab import *
from settings_json import settings_json, board_names
from simulator import simulator

serial_TxQ = deque()
test = SatTest(serial_TxQ)
file_parser = FileParse()

# Notes:
#   - can either call root. or app. methods from kv file.
# to make children of a class do stuff, search for the comments with: '#CDS ' - the number is the step
# recycleview example: https://github.com/kivy/kivy/blob/master/examples/widgets/recycleview/basic_data.py
# thread example: https://github.com/kivy/kivy/wiki/Working-with-Python-threads-inside-a-Kivy-application
# loader example: https://kivy.org/docs/api-kivy.uix.filechooser.html
# useful:   https://stackoverflow.com/questions/46284504/kivy-getting-black-screen
#           https://github.com/kivy/kivy/wiki/Snippets
# https://stackoverflow.com/questions/41290285/kivy-updating-text-with-color-from-python


class Top(BoxLayout):
    uart_tab = ObjectProperty(None)
    sched_tab = ObjectProperty(None)
    resp_tab = ObjectProperty(None)
    dash_tab = ObjectProperty(None)
    stop = threading.Event()

    def __init__(self, **kwargs):
        super(Top, self).__init__(**kwargs)
        self.check_which_port()
        self.setup_tabs()
    
    def setup_tabs(self):
        # since we can't call functions from the constructor of anything but the root element (top), 
        # basically do constructor things here
        self.sched_tab.initialize(serial_TxQ, test)
        self.uart_tab.populate(serial_TxQ)
        self.resp_tab.initialize()
        self.dash_tab.initialize()

        test.attach_dependant(self.resp_tab) # tell the test about resp tab, allows resp tab to receive test data upon update
        test.attach_dependant(self.dash_tab)
        #stdtelem: attach the uart_tab here
        self.start_uart_thread()
  
    def check_which_port(self):
        """ Sets up the UART port based on the settings panel """
        if App.get_running_app().config.get('houston_settings', 'uart_options') == 'Use Manual Entry':
            self.serialPort = App.get_running_app().config.get('houston_settings', 'uart_string')
        else:
            self.serialPort = board_names[App.get_running_app().config.get('houston_settings', 'uart_options')]

    def start_uart_thread(self):
        print('UART thread started')
        threading.Thread(target=self.second_thread).start()

    def second_thread(self):
        while not self.stop.is_set():
            self.reset_serial_flag = False  # if true, will close out the serial 
            self.uart_tab.set_port_info(self.serialPort,'disconnected')   # update the name of the serial port
            if self.serialPort is not 'simulator':
                self.connect_serial()
            else:
                self.sim = simulator()
                self.execute_simulator()
        else:
            return

    def execute_simulator(self):
        self.offset = time.time()               # time we start things up
        self.uart_tab.set_port_info('SIMULATOR','connected')   # update the name of the serial port

        while not self.stop.is_set() and not self.reset_serial_flag:
            # if Houston has something to send, send it
            try:
                cmd = str(serial_TxQ.popleft())
                self.sim.sim_rx(cmd)    # send to simulator
            except IndexError:
                pass 

            # call the simulator, will send out telemetry if it has any
            line = self.sim.sim_tx()
            if line is not None:
                self.dispatch_telem(line)

    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.serialPort, 115200, timeout = 10) 
            self.offset = time.time()               # time we start things up
            self.execute_serial()
          
        except Exception as error:
            if not self.stop.is_set() and not self.reset_serial_flag:
                print(error)
                time.sleep(2)
                self.uart_tab.set_port_info('Waiting for: ' + self.serialPort,'disconnected')   # update the name of the serial port

                print('Waiting for serial...')
                # log.write('Waiting for serial: ' + str(time.time()) + '\r\n')
                self.connect_serial()
        return

    def execute_serial(self):
        while self.ser.isOpen() and not self.stop.is_set() and not self.reset_serial_flag:
            self.uart_tab.set_port_info(self.serialPort,'connected')   # update the name of the serial port

            if self.ser.inWaiting() > 0:             # we've got characters to deal with
                line = self.ser.readline()  
                if len(line.decode('ascii')) > 1:               # this catches the weird glitch where I only get out one character
                    self.dispatch_telem(line)
            else:                               # otherwise, send stuff out if needed
                try:
                    cmd = str(serial_TxQ.popleft())
                    for char in cmd:
                        self.ser.write(char.encode('ascii'))
                        time.sleep(0.05)
                    self.ser.write('\r\n'.encode('ascii')) # sat needs them to consider it a command
                except IndexError:
                    pass            
        else:
            self.ser.close()
            return

    def reset_serial(self, serialPort):
        """ Resets the serial stream when the port is changed in settings """
        self.serialPort = serialPort
        self.reset_serial_flag = True
        print(threading.enumerate())
        
    def dispatch_telem(self, line):
        """ Here we do several different things with the telemetry that comes in """
        try:
            line = line.decode(encoding = 'ascii')
        except: 
            print("Line decode didn't work")
            pass
        print (time.time() - self.offset,':',line)
        self.update_telem_stream(line.expandtabs(tabsize=8)) # expand tabs to get rid of unknown tab char that can come in
        test.check_response(line, time.time())
        file_parser.process_raw(line)

        #TODO: add the telem to a log

    @mainthread
    def update_telem_stream(self, new_text):
        """ called by UART thread, passes data so it can be placed in the UART recycleview"""
        self.uart_tab.insert_end(new_text)
    pass


class HoustonApp(App): # the top level app class
    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.

        # root is a reference to the Top instance, auto populated by Kivy
        self.root.stop.set()
        self.reset_serial_flag = 1
        print("Stopping.")

    def build(self):
        # must immediately return Top() here, cannot do something like self.top = Top, and call other functions      
        return Top()
    
    def build_config(self, config):
        config.setdefaults('houston_settings',{
            'uart_options': 'Please select an option',
            'uart_string': ''
        })

    def build_settings(self, settings):
        """ Load the settings panel layout from settings_json"""
        settings.add_json_panel('Houston Settings', self.config, data = settings_json)

    def on_config_change(self, config, section, key, value):
        """ Called when a setting is changed """
        print(section, config, key, value)
        serialPort = self.root.serialPort
        if key == 'uart_options':
            if board_names[value] is not 'use_man':
                serialPort = board_names[value]
        elif key == 'uart_string':
            serialPort = value
        print('Serial port change: ', serialPort)

        if serialPort != self.root.serialPort: # if we've changed the serial port, reconnect
            self.root.reset_serial(serialPort)
    
    def rm_button_press(self, cmdid): #TODO: is it really required to go up to the app like this?
        self.root.sched_tab.rm_button_press(cmdid)

    def serial_function(self, data):
        print("Serial fun, " + data)

Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    HoustonApp().run()
