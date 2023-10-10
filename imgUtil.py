import os
from os import path
from PIL import Image, ImageTk

from config import ROM_PATH

def findImage(romDir, imgPath):      
    maxWidth = 400
    maxHeight = 400

    fullPath = path.join(romDir, imgPath)        
    if not path.isfile(fullPath):
        return None
    image = Image.open(fullPath)        
    w, h = image.size

    if w >= h and w > maxWidth:
        h = int(h * maxWidth / w)
        w = maxWidth
        image = image.resize((w, h))        
    elif h > w and h > maxHeight:
        w = int(w * maxHeight / h)
        h = maxHeight
        image = image.resize((w, h))    
        
    photo = ImageTk.PhotoImage(image)    
    return photo

