# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 14:24:54 2019

@author: ztomanek
"""

from kivy.vector import Vector
from matplotlib import pyplot as plt

def is_point_on_right(x1, x2, xA, y1, y2, yA):
    v1 = (x2-x1, y2-y1)
    v2 = (x2-xA, y2-yA)
    xp = v1[0]*v2[1] - v1[1]*v2[0]
    
    return xp > 0

def collide_with_track(layer, car):

    cx, cy = car.center
    w, h = car.size
    angle = car.angle
    
    v = Vector(-w/2, h/2).rotate(angle)
    blc = cx + v.x, cy + v.y # bottom left corner
    
    
    v1 = Vector(0, -h).rotate(angle)
    v2 = Vector(w, -h).rotate(angle)
    v3 = Vector(w, 0).rotate(angle)
    
    vectors = [v1, v2, v3]
    x = [blc[0] + _v.x for _v in vectors]
    y = [blc[1] + _v.y for _v in vectors]
    x.append(blc[0])
    y.append(blc[1])
   
    # count bbmax 
    x_min = int(min(x))
    x_max = int(max(x))
    y_min = int(min(y))
    y_max = int(max(y))
    
    lh, lw = layer.shape
    
    err = 0
    vc = Vector(0, 1).rotate(angle) #vector fo cheking side of point towards center
    
    for i in range(x_min, x_max+1):
        for j in range(y_min, y_max+1):
            for k in range(4):
               if not is_point_on_right(x[k], x[(k+1)%4], i, y[k], y[(k+1)%4], j):
                   continue
            if i < lw and j < lh:
                if layer[lh-j][i] > 0:
                    if is_point_on_right(cx, cx-vc.x, i, cy, cy-vc.y, j):
                        err += 1
                    else:
                        err -= 1
                       
                
    return err


class Plotter:
    t = 0
    a_err = 0
    
    time = []
    steering = []
    error = []
    err = []
    
    def refresh(self, err_t, steer):
        self.a_err += err_t
        self.time.append(self.t)
        self.t += 1
        self.err.append(err_t)
        self.error.append(self.a_err)
        self.steering.append(steer)
        
    
    
    def plot(self):
        plt.clf()
        ax = plt.subplot(311)
        
        ax.set_title('Sterowanie')
        ax.plot(self.time, self.steering, color='g')
    
        ax = plt.subplot(312)
        ax.set_title('Blad chwilowy')
        ax.scatter(self.time, self.err, color='r')
    
        ax = plt.subplot(313)
        ax.set_title('Blad calkowity')
        ax.plot(self.time, self.error)
    
        plt.pause(0.01)
    

class PID:
    error = 0
    time = 1
    
    def __init__(self, ki, kp):
        self.ki = ki
        self.kp = kp
    
    def steer(self, err):
        """
        err is the count of pixels that are hit by vehicle. 
        > 0 if they are on right and < 0 otherwise
        
        returns value to turn in angles
        """
        
        self.error += err
        
        return int(self.kp * err) + int((self.ki * self.error)/self.time)