'''
TabbedPanel
============

Test of the widget TabbedPanel.
'''

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.app import ObjectProperty
from kivy.lang import Builder




class Test(TabbedPanel):
    # txt_inpt = ObjectProperty(None)
    #
    # def check_status(self, btn):
    #     print('text input text is: {txt}'.format(txt=self.txt_inpt))

    def on_enter(self, instance, value):
        print('User pressed enter in', instance)



    pass

class TabbedPanelApp(App):
    def build(self):
        return Test()

    def son(self, *args):
        print("hello")




if __name__ == '__main__':
    TabbedPanelApp().run()
