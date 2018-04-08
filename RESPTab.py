# RESPTab

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

class RespTab(TabbedPanelItem):
    resp_rv = ObjectProperty(None)

    # command info is added to here when the commands are uplinked
    # results come in with timestamp

    def __init__(self, **kwargs):
        super(RespTab, self).__init__(**kwargs)

    def update_resp(self):
        self.resp_rv.data.append({'cmdid':str(self.cmdid), 'cmd': self.cmd_entry.text, 'timeout':self.cmd_timeout_entry.text, 'expect': self.cmd_expected_entry.text})
