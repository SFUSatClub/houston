# UARTTab
from functools import partial
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from houston_utils import *
import serial
import queue
from SatTest import *

class UARTTab(TabbedPanelItem):
    rv = ObjectProperty()
    uart_entry = ObjectProperty() # text input box

    def __init__(self, **kwargs):
        super(UARTTab, self).__init__(**kwargs)

    def send_button_press(self, *args):
        print('Sending_button:' + self.uart_entry.text)
        # self.serial_TxQ.put(self.uart_entry.text)
        self.serial_TxQ.append(self.uart_entry.text)

    def on_enter(self, *args): # gets text from the input box on enter
        thing = args[0]
        print('Sending_enter:' + thing.text)
        # self.serial_TxQ.put(thing.text)
        self.serial_TxQ.append(thing.text)


    def populate(self, serial_TxQ):
        self.serial_TxQ = serial_TxQ
        self.rv.data = [{'value': 'init'}]

    def insert_end(self, value):
        self.rv.data.append({'value': value})

    def update(self, value):
        if self.rv.data:
            self.rv.data[0]['value'] = value 
            self.rv.refresh_from_data()
