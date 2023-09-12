from PIL import Image, ImageTk

basePath = 'images/'
from os import path

def findImageFromRomName(romPath, romName):
    imgName = path.splitext(romName)[0] + '.png'
    fullPath = path.join(basePath, romPath, imgName)    
    if not path.exists(fullPath):
        return None
    image = Image.open(fullPath)
    print(image.format, image.size, image.mode)
    photo = ImageTk.PhotoImage(image)
    return photo

