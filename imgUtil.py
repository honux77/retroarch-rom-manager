import os
from os import path
from PIL import Image, ImageTk

def findImage(imgPath):      
    maxWidth = 380
    maxHeight = 380
      
    if not path.isfile(imgPath):
        return None
    image = Image.open(imgPath)        
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

