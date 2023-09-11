#read args from coomand line
import sys
if len(sys.argv) != 2:
    print("Usage: python imgEdit.py <subDir>")
    sys.exit(1)

from os import path
import os

imgDdir = path.join('images/', sys.argv[1])
romDdir = path.join('roms/', sys.argv[1])

roms = [os.path.splitext(f)[0] for f in os.listdir(romDdir)]
imgs = [os.path.splitext(f)[0] for f in os.listdir(imgDdir)]

for f in roms:
    if f not in imgs:
        print("Images not exists: ", f)

    

