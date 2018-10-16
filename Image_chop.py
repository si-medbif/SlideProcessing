import openslide
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

a = openslide.OpenSlide(filename="Path/to/file.svs)#("/Users/dmairiang/Downloads/AFB_5081A.svs")

b = a.read_region((10000,10000),level= 0 ,size= (300,300))

plt.imshow(b)
