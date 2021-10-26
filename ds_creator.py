# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 00:34:11 2021

@author: jano1
"""

import cv2
from PIL import Image
import numpy as np
import glob
import os
import shutil

input_folder = "C:/Users/jano1/Desktop/Neuer Ordner/Rhinoplastic_male_side_CROPPED_AND_SHIFTED"
output_bef = "C:/Users/jano1/Desktop/Neuer Ordner/ds_before_2.npy"
output_aft = "C:/Users/jano1/Desktop/Neuer Ordner/ds_after_2.npy"
    
imgs_before = glob.glob(input_folder + "/*/BEFORE.png")   
imgs_after = glob.glob(input_folder + "/*/AFTER.png")   

bef_list = []
aft_list = []

for image in imgs_before:
    bef_list.append(cv2.cvtColor(cv2.imread(image), cv2.COLOR_BGR2RGB))
bef_arr = np.array(bef_list)
np.save(output_bef, bef_arr)
    
for image in imgs_after:
    aft_list.append(cv2.cvtColor(cv2.imread(image), cv2.COLOR_BGR2RGB))
aft_arr = np.array(aft_list)
np.save(output_aft, aft_arr)
   