import os
from os import path
from PIL import Image, ImageTk

basePath = 'images/'

def findImageFromRomName(romPath, romName):
    imgName = path.splitext(romName)[0] + '.png'
    fullPath = path.join(basePath, romPath, imgName)    
    if not path.exists(fullPath):
        return None
    image = Image.open(fullPath)    
    photo = ImageTk.PhotoImage(image)    
    return photo

