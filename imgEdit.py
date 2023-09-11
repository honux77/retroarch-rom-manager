# read png from current directory and edit it
# save it as a new png file

from PIL import Image

#read args from coomand line
import sys
if len(sys.argv) != 2:
    print("Usage: python imgEdit.py <subDir>")
    sys.exit(1)

from os import path

subdir = path.join('images/', sys.argv[1])

# open images from current directory
import os
from os import path
os.chdir(subdir)

files = [f for f in os.listdir() if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.gif')]

def changeImg(f1, f2):
    img = Image.open(f1)    

    # get the size of the image
    width, height = img.size
    print("width: ", width)
    print("height: ", height)

    # get the pixel value
    pixels = img.load()
    print("pixel value: ", pixels[0,0])

    # resize image by width
    # w: h = 240: x,  x = 240 * h / w
    if width > height:
        img = img.resize(size = (240 * width // height, 240))
    else:
        img = img.resize(size = (240, 240 * height // width))

    # crop images by width and height
    img = img.crop((0, 0, 240, 240))

    #img.save('zzz_' + f)
 
    img.save(f2)
    if f1 != f2:
        os.remove(f1)

for f in files:
    print(f)              
    f2 = f
    if f.endswith('.jpg') or f.endswith('.gif'):
        f2 = f2[:-4] + '.png'
    changeImg(f, f2)
