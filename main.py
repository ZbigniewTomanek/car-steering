# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 10:17:02 2019

@author: ztomanek
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
        NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
        )
from kivy.vector import Vector
from kivy.clock import Clock
from math import sin, cos, radians
from kivy.core.window import Window
from kivy.graphics import Color, Line
from steering import collide_with_track, Plotter

import imageio

MAP_FILENAME = 'track.png'


class Car(Widget):
    visible = BooleanProperty(True)
    angle = NumericProperty(90)
    vx = NumericProperty(0)
    vy = NumericProperty(0)
    velocity = ReferenceListProperty(vx, vy)
    
    def turn(self, angle):
        self.vx, self.vy = Vector(*self.velocity).rotate(angle)
        self.angle += round(angle)
        
        
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        
    def accelerate(self, delta):
        self.vx += cos(radians(self.angle)) * delta
        self.vy += sin(radians(self.angle)) * delta
        self.move()
        
        

class TrackPainter(Widget):
    enabled = True
    
    def on_touch_down(self, touch):
        if self.enabled:
            with self.canvas:
                Color(1, 1, 0)
                touch.ud['line'] = Line(points=(touch.x, touch.y))
            
    def on_touch_move(self, touch):
        if self.enabled:
            touch.ud['line'].points += [touch.x, touch.y]
        
    def load_bitmap(self):
        self.export_to_png(MAP_FILENAME)
        return imageio.imread(MAP_FILENAME)[:,:,0]
    
        
class CarSimulation(Widget):
    car = ObjectProperty(None)
    bitmap = None
    p = Plotter()
    
    def __init__(self, **kwargs):
        super(CarSimulation, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        self.tpainter = TrackPainter(size=(800, 600))
        self.add_widget(self.tpainter)
        
        print(self.size)
        
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
        

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        c = keycode[1]
        
        if self.bitmap is None:
            if c == 'spacebar':
                self.bitmap = self.tpainter.load_bitmap()
                self.tpainter.enabled = False
            elif c == 'backspace':
                self.tpainter.canvas.clear()
        else:
            print(self.car.pos)
            if c == 'w':
                self.car.accelerate(1)
            elif c == 's':
                self.car.accelerate(-1)
            elif c == 'd':
                err = collide_with_track(self.bitmap, self.car)
                self.car.turn(-5)
                self.p.refresh(err, -5)
            elif c == 'a':
                err = collide_with_track(self.bitmap, self.car)
                self.car.turn(5)
                self.p.refresh(err, 5)
            elif c == 'p':
                self.p.plot()
        return True
    
    def init(self):
        self.car.center = self.center
        self.car.vx = 0
        self.car.vy = 0

    def update(self, dt):
        self.car.move()
        if self.bitmap is not None:
            err = collide_with_track(self.bitmap, self.car)
            self.p.refresh(err, 0)
            if err != 0:
                print(err)
                self.car.vy = 0
                self.car.vx = 0
           
                
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