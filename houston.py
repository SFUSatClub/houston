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
# to make children of a class do stuff, search for the comments with: '#CDS ' - the number is the step
# recycleview example: https://github.com/kivy/kivy/blob/master/examples/widgets/recycleview/basic_data.py


class MainTab(BoxLayout):
    label_wid = ObjectProperty()
    rv_handle = ObjectProperty() #CDS 3 - assign objectproperty to the handle

    def button_press(self, *args):
        print("hello")

    def on_enter(self, *args): # gets text from the input box on enter
        thing = args[0]
        print(thing.text)

    def do_stuff(self, input):
        self.label_wid.text = input
        print("callsed")

    def rv_do_sthng(self):
        self.rv_handle.rv_foo("rv hello") #CDS 4 - use the object handle to call methods of that class

class TPI1(TabbedPanelItem):
    def __init__(self):
        TabbedPanelItem.__init__(self)
        self.mt1 = MainTab()
        self.add_widget(self.mt1)

class TPI2(TabbedPanelItem):
    def __init__(self):
        TabbedPanelItem.__init__(self)


items = [0, "apple", "dog", 1, "banana", "cat", 2, "pear", "rat", 3,  "pineapple", "bat"]

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in items]

    def rv_foo(self, input):
        print(input)
        # thingy =[4, "airplane", "hello",]
        # self.data.append({'text': str(x)} for x in thingy)
        # print(self.data)

class Top(TabbedPanel): # top of the visual hierarchy, builds the tabbed panels
    def __init__(self):
        self.stop = threading.Event()
        TabbedPanel.__init__(self)

# Create tabbed panel item instances so we can reference their children
        self.tpi1 = TPI1()
        self.add_widget(self.tpi1)
        self.tpi2 = TPI2()
        self.add_widget(self.tpi2)

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
        # print(self.ids.lb1.text)
        # self.ids.lb1.text = new_text
        self.tpi1.mt1.ids.lab_2.text = new_text #going down through the hierarchy to access a property
        self.tpi2.ids.lb1.text = new_text # a top level ish label
        self.tpi1.mt1.do_stuff(str(random.random() * 100)) # this one demonstrates using the object property passup thing
        self.tpi1.mt1.rv_do_sthng() #CDS 6 - going down in the hierarchy a little, call the method that pokes down into the child object's methods
        # print(self.tpi2.children)
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
