# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 10:17:02 2019

@author: ztomanek
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
        NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
        )
from kivy.vector import Vector
from kivy.clock import Clock
from math import sin, cos, radians
from kivy.core.window import Window
from kivy.graphics import Color, Line, Ellipse
from steering import collide_with_track, Plotter, PID, count_ray_error
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
        self.move()
        
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        
    def accelerate(self, delta):
        self.vx += cos(radians(self.angle)) * delta
        self.vy += sin(radians(self.angle)) * delta
        self.move()
        
        

class TrackPainter(Widget):
    lines = []
    
    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 1, 0)
            touch.ud['line'] = Line(points=(touch.x, touch.y))
                
    def draw_points(self, points):
        self.points = points
        self.canvas.clear()
        
        with self.canvas:
                Color(1, 1, 0)
                for l in self.lines:
                    Line(points=l)
                
                Color(1, 0, 0)
                for p in points:
                    Ellipse(pos=(p[0] - 2.5, p[1] - 2.5), size=(5, 5))
                
                
            
    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]
            
            
    def on_touch_up(self, touch):
        self.lines.append(touch.ud['line'].points)
        
    def load_bitmap(self):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 0)
            for l in self.lines:
                Line(points=l)
                    
        self.export_to_png(MAP_FILENAME)
        return imageio.imread(MAP_FILENAME)[:,:,0]
    
    def clear(self):
        self.lines.clear()
        self.canvas.clear()
    
        
class CarSimulation(Widget):
    car = ObjectProperty(None)
    
    speed = 1
    bitmap = None
    
    p = Plotter()
    controller = ObjectProperty(None)
    pid = BooleanProperty(False)
    K = -0.01
    
    kp = NumericProperty(0)
    ki = NumericProperty(0)
    kd = NumericProperty(0)
        
    
    def __init__(self, **kwargs):
        super(CarSimulation, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        Window.size = (800, 600)
        
        self.tpainter = TrackPainter(size=(800, 600))
        self.add_widget(self.tpainter)
                
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
        

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        c = keycode[1]
        
        if not self.pid: # manual mode
            if c == 'w':

                self.car.accelerate(self.speed)
            elif c == 's':
                self.car.accelerate(-self.speed)
            elif c == 'd':
                err = collide_with_track(self.bitmap, self.car)
                self.car.turn(-5)
                self.p.refresh(err, -5)
            elif c == 'a': 
                err = collide_with_track(self.bitmap, self.car)
                self.car.turn(5)
                self.p.refresh(err, 5)
            elif c == 'k':
                print('pid mode')
                self.init_pid(-45, 45)
                self.pid = True
                
                
        elif c == 'k':
             print('manual mode')
             self.pid = False
             self.controller = ObjectProperty(None)
        elif c == 'z':
            self.set_pid(self.K*1.2)
        elif c == 'x':
            self.set_pid(self.K/1.2)
        if c == 'p':
            self.p.plot()
        elif c == 'spacebar':
            self.car.center = self.center
            self.car.vx = 0
            self.car.vy = 0
        elif c == 'backspace':
                self.tpainter.clear()
                self.bitmap = self.tpainter.load_bitmap()
    
        return True
    
    def on_touch_up(self, touch):
        self.tpainter.on_touch_up(touch)
        self.bitmap = self.tpainter.load_bitmap()
        
    def on_touch_down(self, touch):
        self.tpainter.on_touch_down(touch)
    
    def on_touch_move(self, touch):
        self.tpainter.on_touch_move(touch)
    
    def set_pid(self, K):
        self.K = K
        self.controller.set_tunings(1.2 * self.K, 0,0)
        self.kp = self.controller.kp
        self.ki = self.controller.ki
        self.kd = self.controller.kd
    
    def init_pid(self, o_min, o_max):
        self.controller = PID(1.2 * self.K, 0, 0, o_min, o_max)
        
        self.kp = self.controller.kp
        self.ki = self.controller.ki
        self.kd = self.controller.kd
        
        self.car.accelerate(self.speed)
    
    def init(self):
        self.bitmap = self.tpainter.load_bitmap()
        self.car.center = self.center
        self.car.vx = 0
        self.car.vy = 0

    def update(self, dt):
        if self.bitmap is not None:
            self.car.move()
            coll = collide_with_track(self.bitmap, self.car)
            err, points = count_ray_error(self.bitmap, self.car)
            self.tpainter.draw_points(points)
            
            dec = 0
            if self.pid:
                if self.controller.is_ready():
                    dec = self.controller.steer(err)
                    if dec != 0:
                        print(dec, err)
                    self.car.turn(dec)
            else:
                if coll: # if car is in manual mode stop the car on collision
                    self.car.vy = 0
                    self.car.vx = 0
                
                
            self.p.refresh(err, dec)
            
           
                
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