# -*- coding: utf-8 -*-
"""
Created on Wed May 22 18:14:58 2019

@author: Joni Väätäinen
"""

import argparse
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt 
from PIL import Image

# get file path    
parser = argparse.ArgumentParser()
parser.add_argument("-s",'--size', nargs='+', required=True, type=int, help="New width and height of images")
parser.add_argument("-i",'--input-path', type=str, default='./resize',help="Path to dir with target images")
parser.add_argument("-o",'--output-path', type=str, default='./resized',help="Path to dir for saving resized images")
args = parser.parse_args()

resize_dir = args.input_path
resized_dir = args.output_path

if not os.path.exists(resized_dir):
    os.makedirs(resized_dir)
    
image_files = os.listdir(resize_dir)
images = []
depth_images = []
depth_images_pre = []
img_size = tuple(args.size)

for img_file in image_files:
    name, ext = os.path.splitext(img_file)
    
    if (ext == ".png" or ext == ".jpg") and not name.endswith("depth"):
        image = cv2.imread(os.path.join(resize_dir,img_file))
        image_resized = cv2.resize(image,(img_size))
        cv2.imwrite(os.path.join(resized_dir,img_file),image_resized)
    elif ext == ".tiff":
        depth_image = Image.open(os.path.join(resize_dir,img_file))
        depth_image = np.array(depth_image)
        depth_resized = cv2.resize(depth_image,(img_size))
        np.save(os.path.join(resized_dir,name),depth_resized)
        
        