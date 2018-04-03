'''
SFUSat Houston
============
Author: Richard Arthurs
April 2018

Ground control app for CubeSat.
'''

import threading
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem

from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
import time
import random
from kivy.clock import Clock, mainthread
from kivy.app import ObjectProperty
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

# Notes:
#   - can either call root. or app. methods from kv file.

class MainTab(BoxLayout):
    def button_press(self, *args):
        print("hello")

    def on_enter(self, *args): # gets text from the input box on enter
        thing = args[0]
        print(thing.text)

#
# class TabPan1(TabbedPanelItem):
#     pass



class Top(TabbedPanel): # top of the visual hierarchy, builds the tabbed panels
    def __init__(self):
        self.stop = threading.Event()
        TabbedPanel.__init__(self)
        self.start_second_thread("dfjh")

    def start_second_thread(self, l_text):
        threading.Thread(target=self.second_thread, args=(l_text,)).start()

    def second_thread(self, label_text):
         while True:
            if self.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            print("second thread")
            self.update_label_text(str(random.random() * 100))

            time.sleep(3)


    @mainthread
    def update_label_text(self, new_text):
        print(self.ids.lb1.text)
        self.ids.lb1.text = new_text

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
