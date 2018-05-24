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

class DASHTab(TabbedPanelItem):

    def __init__(self, **kwargs):
        super(DASHTab, self).__init__(**kwargs)

    def initialize(self):
        pass

    def update_from_sattest(self, sattest, method):
      pass

