'''
TabbedPanel
============

Test of the widget TabbedPanel.
'''

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.app import ObjectProperty
from kivy.lang import Builder


class MainTab(BoxLayout):
    def on_enter(self, instance, value):
        print('User pressed enter in', instance)


class Test(TabbedPanel):

    def on_enter(instance, value):
        print('User pressed enter in', instance)
    textinput = TextInput(text='Hello world', multiline=False)

    textinput.bind(on_text_validate=on_enter)
    # txt_inpt = ObjectProperty(None)
    #
    # def check_status(self, btn):
    #     print('text input text is: {txt}'.format(txt=self.txt_inpt))




    pass

class TabbedPanelApp(App):
    def build(self):
        return Test()

    def son(self, *args):
        print("hello")




if __name__ == '__main__':
    TabbedPanelApp().run()
