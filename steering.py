# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 14:24:54 2019

@author: ztomanek
"""

from kivy.vector import Vector
from matplotlib import pyplot as plt
import time
import math

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
    
    #err = 0
    #vc = Vector(0, 1).rotate(angle) #vector fo cheking side of point towards center
    #vcp = Vector(-1, 0).rotate(angle)
    
    for i in range(x_min, x_max+1):
        for j in range(y_min, y_max+1):
            for k in range(4):
               if not is_point_on_right(x[k], x[(k+1)%4], i, y[k], y[(k+1)%4], j):
                   continue
            if i < lw and 0 < j < lh:
                if layer[lh-j][i] > 0:
                    return True
                    
                    #if is_point_on_right(cx, cx - vcp.x, i, cy, cy - vcp.y, j):
                        #print('Z przodu!')
                        #if is_point_on_right(cx, cx-vc.x, i, cy, cy-vc.y, j):
                            #print('prawo')
                            #err -= 1
                        #else:
                            #print('lewo')
                            #err += 1
                    #else:
                        #print('z tylu')
                       
    return False


def count_ray_error(layer, car, max_distance=40, angle_delta=20):
    cx, cy = car.center
    cw, ch = car.size
    lh, lw = layer.shape
    err = 0
    
    min_d = round(math.sqrt((cw/2)**2 + (ch/2)**2)) # dystans od którego będzie sprawdzany
    sv = Vector(0, -1).rotate(car.angle)
    
    points_x = []
    points_y = []
    
    for angle in range(0, 181, angle_delta):
        #shift center outside a car
        sx = cx + sv.x * min_d
        sy = cy + sv.y * min_d
        dis = max_distance
        
        found = False
        for d in range(0, max_distance):
            py = int(sy + sv.y * d)
            px = int(sx + sv.x * d)
            
            if px >= lw or lh-py >= lh:
                points_x.append(px)
                points_y.append(py)
                found = True
                dis = d
                break
                
            if layer[lh-py][px] > 0:
                # ray found nearest point
                points_x.append(px)
                points_y.append(py)
                found = True
                dis = d
                break
        
        if not found:
            points_x.append(sx + sv.x * max_distance)
            points_y.append(sy + sv.y * max_distance)
            
        sv = sv.rotate(angle_delta)
        
        if angle < 90:
            err += (dis - max_distance)**2
        else:
            err -= (dis - max_distance)**2
            
    return err, list(zip(points_x, points_y))
                
            
    


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
        ax.plot(self.time, self.err, color='r')
    
        ax = plt.subplot(313)
        ax.set_title('Blad calkowity')
        ax.plot(self.time, self.error)
    
        plt.pause(0.01)
    

class PID:
    integral_sum = 0
    
    sample_time = 0
    setpoint = 0
    last_time = 0
    last_input = 0
    
    o_min = 0
    o_max = 0
    
    def __init__(self, kp, ki, kd, out_min, out_max, sample=0.1):
        self.sample_time = sample
        
        if out_min > out_max:
            raise ValueError
            
        self.o_min = out_min
        self.o_max = out_max
        self.set_tunings(kp, ki, kd)
        
    def set_tunings(self, kp, ki, kd):
        sample_in_sec = self.sample_time / 1000
        self.kp = kp
        self.ki = ki * sample_in_sec
        self.kd = kd / sample_in_sec
        
        
    def is_ready(self):
        return time.time() - self.last_time >= self.sample_time
    
    def steer(self, inpt):
        err = self.setpoint - inpt
        
        self.integral_sum += self.ki * err
        if self.integral_sum > self.o_max:
            self.integral_sum = self.o_max
        
        d_input = inpt - self.last_input
        
        output = self.kp * err + self.integral_sum + self.kd * d_input
        
        if output > self.o_max:
            output = self.o_max
        elif output < self.o_min:
            output = self.o_min
        
        self.last_time = time.time()
        self.last_input = inpt
        
        return output