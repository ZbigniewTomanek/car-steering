# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 14:24:54 2019

@author: ztomanek
"""

import numpy as np
from kivy.vector import Vector
    
def collide_with_track(bitmap, pos, size, angle):
    posx, posy = pos
    w,h = size
    
    layer = bitmap[:, :, 0]
    
    x1 = posx
    x2 = posx + w
    
    y1 = posy
    y2 = posy + h
    
    