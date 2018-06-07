# UARTTab
from functools import partial
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty
from kivy.app import StringProperty
from kivy.properties import ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from houston_utils import *
import serial
import queue
from SatTest import *

class UARTTab(TabbedPanelItem):
    rv = ObjectProperty()
    uart_entry = ObjectProperty()   # text input box
    port_label = StringProperty()   # port status label
    port_label_color = ListProperty()

    def __init__(self, **kwargs):
        super(UARTTab, self).__init__(**kwargs)
        self.port_label = "Disconnected"
        self.port_label_color = (1,0.2,0.4,1) # pink-red ish

    def set_port_info(self,portname,status):
        """ set the text/colour of the port label """
        self.port_label = portname
        if status == "connected":
            self.port_label_color = (0.2,1,0.4,1) # green ish
        else:
            self.port_label_color = (1,0.2,0.4,1) # pink-red ish

    def send_button_press(self, *args):
        print('Sending_button:' + self.uart_entry.text)
        self.serial_TxQ.append(self.uart_entry.text)

    def on_enter(self, *args): # gets text from the input box on enter
        thing = args[0]
        print('Sending_enter:' + thing.text)
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

    #stdtelem: implement the update_from_sattest method as is done in RESPtab
    # in this case, look for stdtelem flag from the method, and update the graphics based on the data

