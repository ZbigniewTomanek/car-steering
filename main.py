# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 10:17:02 2019

@author: ztomanek
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
        NumericProperty, ReferenceListProperty, ObjectProperty
        )
from kivy.vector import Vector
from kivy.clock import Clock
from math import sin, cos, radians
from kivy.core.window import Window


class Car(Widget):
    angle = NumericProperty(90)
    vx = NumericProperty(0)
    vy = NumericProperty(0)
    velocity = ReferenceListProperty(vx, vy)
    
    def turn(self, angle):
        self.vx, self.vy = Vector(*self.velocity).rotate(angle)
        self.angle += round(angle)
        
    
    def move(self, delta):
        self.vx += cos(radians(self.angle)) * delta
        self.vy += sin(radians(self.angle)) * delta
        self.pos = Vector(*self.velocity) + self.pos
        
class CarSimulation(Widget):
    car = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(CarSimulation, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print(self.car.vx, self.car.vy)
        if keycode[1] == 'w':
            self.car.move(1)
        elif keycode[1] == 's':
            self.car.move(-1)
        elif keycode[1] == 'd':
            self.car.turn(-5)
        elif keycode[1] == 'a':
            self.car.turn(5)
        return True
    
    def init(self):
        self.car.center = self.center
        self.car.vx = 0
        self.car.vy = 0

    def update(self, dt):
   
        self.car.move(0)


        if (self.car.y < 0) or (self.car.top > self.height):
            self.car.vy = 0
            self.car.vx = 0

        if (self.car.x < 0) or (self.car.right > self.width):
            self.car.vy = 0
            self.car.vx = 0

class CarApp(App):
    def build(self):
        sim = CarSimulation()
        sim.init()
        Clock.schedule_interval(sim.update, 1.0/60.0)
        return sim
    
if __name__ == '__main__':
    CarApp().run()