# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 20:26:22 2021

@author: jano1
"""

from PIL import Image
import numpy as np
import glob
import os
import shutil

input_folder = "C:/Users/jano1/Desktop/Neuer Ordner/Rhinoplastic_male_side_SORTED"
output_folder = "C:/Users/jano1/Desktop/Neuer Ordner/Rhinoplastic_man_side_CHOPPED"

if not os.path.exists(output_folder):
    os.mkdir(output_folder)
    
imgs_before = glob.glob(input_folder + "/*/*before*")    

for img_before in imgs_before:
    print(img_before)
    folder_path = os.path.dirname(img_before)
    folder_name = os.path.basename(folder_path)
    if not os.path.exists(output_folder+"/"+folder_name):
        os.mkdir(output_folder+"/"+folder_name)
    after_file = glob.glob(folder_path + "/*after*")
    if len(after_file)>0:
        after_file = after_file[0]
        img_left = Image.open(img_before)
        img_right = Image.open(after_file)
        img_right.save(output_folder+"/"+folder_name + "/AFTER.png")
        img_left.save(output_folder+"/"+folder_name + "/BEFORE.png")
    else:
        img = Image.open(img_before)
        img_array = np.array(img)
        x_len = img_array.shape[1]
        middle = int(x_len/2)
        data_left = img_array[:, 0:middle, :]
        data_right = img_array[:, middle::, :]
        img_left = Image.fromarray(data_left)
        img_right = Image.fromarray(data_right)
        img_right.save(output_folder+"/"+folder_name + "/AFTER.png")
        img_left.save(output_folder+"/"+folder_name + "/BEFORE.png")
        

