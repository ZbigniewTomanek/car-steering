# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 10:17:02 2019

@author: ztomanek
"""

from kivy.app import App
from kivy.uix.widget import Widget

class CarSimulation(Widget):
    pass

class CarApp(App):
    def build(self):
        return CarSimulation()
    
if __name__ == '__main__':
    CarApp().run()