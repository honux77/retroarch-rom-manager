import os

import tkinter as tk
from tkinter import filedialog

def openFileDialog(currentDir=None):
    if currentDir == None:
        currentDir = "./"
    filepath = filedialog.askdirectory(
        title="기본 폴더를 선택하세요",
        initialdir=currentDir,
    )
    
    if filepath:
        print(f"선택된 폴더: {filepath}")
        dirs = os.listdir(filepath)
        if "roms" in dirs and "images" in dirs:
            return filepath
        else:
            print("선택된 폴더가 유효하지 않습니다.")
            return None
    else:
        print("파일 선택 취소")
        return None
