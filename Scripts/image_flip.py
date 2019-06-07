#!/usr/bin/env python
from PIL import Image
import os

def switch(option):
    switcher = {
        1: Image.FLIP_LEFT_RIGHT,
        2: Image.FLIP_TOP_BOTTOM,
        3: Image.ROTATE_90,
        4: Image.ROTATE_180,
        5: Image.ROTATE_270
    }
    # Get the function from switcher dictionary
    res = switcher.get(option, lambda: "nothing")
    # Execute the function
    return res

def flip_image(image_path, option = 1,saved_location = ''):
    fimage_path = os.path.abspath(image_path)
    image_obj = Image.open(fimage_path)
    rotated_image = image_obj.transpose(switch(option))
    if saved_location != '':
        rotated_image.save(saved_location)
        return
    else:
        return rotated_image
        
