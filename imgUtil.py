import os
from os import path
from PIL import Image, ImageTk

from config import IMAGE_PATH

def findImage(romPath, imgName):    
    fullPath = path.join(IMAGE_PATH, romPath, imgName)    
    if not path.exists(fullPath):
        return None
    image = Image.open(fullPath)    
    photo = ImageTk.PhotoImage(image)    
    return photo

