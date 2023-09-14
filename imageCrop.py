import os
from os import path
import tkinter as tk
from PIL import Image, ImageTk

from config import IMAGE_PATH, ROM_PATH, EXT

# resize and crop all images in a folder
def resizeAndCropAll(gamePath, msgTextBox:tk.Text):
    currDir = os.getcwd()
    # delete textBox content
    msgTextBox.delete(1.0, tk.END)
    msgTextBox.insert(tk.INSERT, "===이미지 리사이즈 및 크롭 시작===\n")    

    # save it as a new png file
    subdir = path.join(IMAGE_PATH, gamePath)
    os.chdir(subdir)
    # get all files in current directory
    files = [f for f in os.listdir() if os.path.isfile(f) and (f.endswith('.png') or f.endswith('.jpg') or f.endswith('.gif'))]
    
    n = 0
    for f in files:    
        n += _changeImg(f, msgTextBox)

    msgTextBox.insert(tk.INSERT, "{} 이미지가 변환되었습니다.".format(n))
    os.chdir(currDir)    

def _changeImg(f, msgTextBox:tk.Text):
    img = Image.open(f)    
    width, height = img.size
    
    if width == 240 and height == 240:
        msgTextBox.insert(tk.INSERT, "{} 는 이미 240x240 입니다.\n".format(f))        
        return
    
    cx, cy = width // 2, height // 2

    # make it square
    if width > height:
        img = img.crop((cx - cy, 0, cx + cy, height))
    else:
        img = img.crop((0, cy - cx, width, cy + cx))
    
    img = img.resize(size = (240, 240))

    # if not png, convert it to png and delete original file
    if f.endswith(('png')):
        msgTextBox.insert(tk.INSERT, "{} 를 240x240 크롭 완료\n".format(f))
        img.save(f)
    else:
        newFile = f[:-4] + '.png'
        img.save(newFile)
        msgTextBox.insert(tk.INSERT, "{} 를 240x240 크롭 및 PNG 변환 완료\n".format(newFile))
        os.remove(f)
        msgTextBox.insert(tk.INSERT, "{} 삭제 완료\n".format(f))
    