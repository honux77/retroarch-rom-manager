import os
from os import path
import re
import tkinter as tk
from tkinter import messagebox as mBox

from config import ROM_PATH, IMAGE_PATH, EXT


def findSimilarImage(romName, allImages):
    '''
    romName과 가장 유사한 이미지 파일명을 찾아서 반환한다.
    romName: 롬 파일명
    allImages: 이미지 파일명 리스트
    '''
    import fuzzywuzzy.process as fuzzProcess
    return fuzzProcess.extractOne(romName, allImages)

def getRomList(dirName):
    dir = path.join(ROM_PATH, dirName)
    roms = [f for f in os.listdir(dir) if f.endswith(EXT[dirName])]    
    return roms


def getImgList(dirName):
    import os
    from os import path
    dir = path.join(IMAGE_PATH, dirName)
    imgs = [f for f in os.listdir(dir) if f.endswith('.png')]
    return imgs

def imageDelete(imgPath, romPath):
    import os
    from os import path

    roms = [os.path.splitext(f)[0] for f in os.listdir(romPath)]
    imgs = [os.path.splitext(f)[0] for f in os.listdir(imgPath)]

    for f in imgs:
        if f not in roms:
            print("Roms not exists: ", f)
            os.remove(path.join(imgPath, f + '.png'))


def printRomInfo(imgPath, romPath):
    import os
    from os import path

    roms = [os.path.splitext(f)[0] for f in os.listdir(romPath)]
    imgs = [os.path.splitext(f)[0] for f in os.listdir(imgPath)]

    for f in roms:
        if f not in imgs:
            print("Image not exists: ", f)

def deleteRomAndImages(subPath, romName):
    msg = ""
    result = mBox.askquestion("삭제", "선택된 롬과 이미지를 삭제하시겠습니까?")
    rom = path.join('roms/', subPath, romName)
    name = path.splitext(romName)[0]
    img = path.join('images/', subPath, name + '.png')
    os.remove(rom)
    try:
        os.remove(img)    
    except:
        return "이미지 삭제 실패"
    return romName + " 삭제 성공"

# main function for test
if __name__ == "__main__":
    print("Test getRomList")
    print(getRomList('fc'))