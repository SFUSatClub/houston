# RESPTab

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior

import random
import time

class RESPTab(TabbedPanelItem):
    resp_rv = ObjectProperty(None)

    # command info is added to here when the commands are uplinked
    # results come in with timestamp

    def __init__(self, **kwargs):
        super(RESPTab, self).__init__(**kwargs)

    def initialize(self):
        pass
        # self.test = test # the test handler for the application

    def update_from_sattest(self, sattest, method):
        self.clear_resp() # dump everything before we update
        # if method == 'add_schedule'
        for item in sattest.new:
            dct = item.cmd_dict()
            self.append_resp(dct)

        for item in sattest.pending:
            dct = item.cmd_dict()
            self.append_resp(dct)

        for item in sattest.acknowledged:
            dct = item.cmd_dict()
            self.append_resp(dct)
 
        for item in sattest.errored:
            dct = item.cmd_dict()
            self.append_resp(dct)


    def append_resp(self, stuff):
        self.resp_rv.data.append(stuff)

    def clear_resp(self):
        del self.resp_rv.data[:] # need to do it this way so that all references are deleted - "deep delete"

# class Resprow(RecycleDataViewBehavior):
#     ''' Add selection support to the Label '''
#     index = NumericProperty(0)

#     cmdid = NumericProperty(0)
#     cmd = StringProperty()
#     timeout = NumericProperty(0)
#     expect = StringProperty()
#     epoch = NumericProperty(0)
#     rel = BooleanProperty(True)
#     expect = StringProperty()

    
    # def refresh_view_attrs(self, rv, index, data):
    #     ''' Catch and handle the view changes '''
    #     self.index = index
    #     # self.cmdid = data['cmdid']
    #     # print(self.colours[self.state][0])
    #     # self.r = self.colours[self.state][0]
    #     # print(self.r)
    #     # self.r = self.colours[self.state](1)
    #     # self.r = self.colours[self.state](2)
    #     print("refresh called -----------------")
        
    #     # self.my_colour = self.colours[self.state]
    #     return super(SelectableLabel, self).refresh_view_attrs(
    #         rv, index, data)
