#!/usr/bin/env python
from PIL import Image
import os
import argparse

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

def flip_image(fimage_path, option, saved_location = ''):
    
    image_obj = Image.open(fimage_path)
    rotated_image = image_obj.transpose(switch(option))
    if saved_location != '':
        rotated_image.save(saved_location)
        return
    else:
        return rotated_image

def main(args):
    fimage_path = os.path.abspath(args.image_path)
    flip_image(fimage_path, args.option, args.saved_location)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-i",
        "--image_path",
        action="store",
        help="Name and path of the image file"
    )
    
    parser.add_argument(
        "-o",
        "--option",
        action="store",
        type = int,
        choices=[1,2,3,4,5],
        default=1,
        help="Method for rotate/flip the image. 1 = Flip horizontally, 2= Flip vertically, 3 = Rotate 90 deg, 4 = Rotate 180 deg, 5 = Rotate 270 deg"
    )
    
    parser.add_argument(
        "-s",
        "--saved_location",
        action="store",
        help="Name of the destination path/file for saving the image"
    )
    
    args = parser.parse_args()
    main(args)
