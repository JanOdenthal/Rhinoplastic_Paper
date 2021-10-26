# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 22:02:05 2021

@author: jano1
"""

import cv2
from PIL import Image
import numpy as np
import glob
import os
import shutil

input_folder = "C:/Users/jano1/Desktop/Neuer Ordner/Rhinoplastic_man_side_CHOPPED"
output_folder = "C:/Users/jano1/Desktop/Neuer Ordner/Rhinoplastic_male_side_CROPPED_AND_SHIFTED"

if not os.path.exists(output_folder):
    os.mkdir(output_folder)
    
imgs_before = glob.glob(input_folder + "/*/BEFORE.png")   
imgs_after = glob.glob(input_folder + "/*/AFTER.png")   
imgs = imgs_before + imgs_after

# Load the cascade
face_cascade = cv2.CascadeClassifier('C:/Users/jano1/Desktop/OpenCv/opencv-master/data/haarcascades/haarcascade_profileface.xml')
cc = 0
ii = 0

def crop(path):
    image = cv2.imread(path)
    color_x, color_y = np.where(np.any(image < 230, axis=2))
    x0 = color_x.min()
    x1 = color_x.max()
    y0 = color_y.min()
    y1 = color_y.max()
    cropped_image = image[x0:x1 + 1, y0:y1 + 1]
    return cropped_image

for image in imgs:
    print(cc)
    image_name = os.path.basename(image)
    folder_path = os.path.dirname(image)
    folder_name = os.path.basename(folder_path)
    img = crop(image)
    if not os.path.exists(output_folder+"/"+folder_name):
        os.mkdir(output_folder+"/"+folder_name)
    x = img.shape[1]
    y = img.shape[0]
    middle_x = int(x/2)
    middle_y = int(y/2)
    ruler = min([middle_x, middle_y])
    crop_img = img[middle_y-ruler:middle_y+ruler, middle_x-ruler:middle_x+ruler]
    crop_img = cv2.resize(crop_img, (256, 256)) 
    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
    imag = Image.fromarray(crop_img)
    cv2.imshow('c', crop_img)
    imag.save(output_folder+"/"+folder_name + "/" + image_name)
    cc = cc+1
