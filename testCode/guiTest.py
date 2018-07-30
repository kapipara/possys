import kivy
kivy.require('1.9.2')
from kivy.app import App
from kivy.uix.label import Label

class MyApp(App):
    def build(self):
        return Label(text="Hello World!",font_size="48sp")

if __name__ == '__main__'
    MyApp().run()