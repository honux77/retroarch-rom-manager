# simple gui apllication

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as mBox

from PIL import ImageTk, Image

# Create instance
win = tk.Tk()

# Add a title
win.title("Famliy Pocket Rom Manager")

# roms 폴더의 서브 폴더들을 읽어서 드롭리스트에 추가
import os
from os import path
subdirs = [f for f in os.listdir('roms/') if path.isdir(path.join('roms/', f))]

# Set size of window
win.geometry("1024x768")

# event handler for select_button
def listSelectedDir(event):
    dir = romBox.get()
    import fileUtil
    romList = fileUtil.getRomList(dir)
    
    # get image list and cut extension
    imgNameList = [path.splitext(f)[0] for f in fileUtil.getImgList(dir)]
    
    # add romList to romListBox
    romListBox.delete(0, tk.END)    

    #delete noImageTextBox
    noImageTextBox.delete(1.0, tk.END)

    for rom in romList:
        romName = path.splitext(rom)[0]
        romListBox.insert(tk.END, rom)                    
        
        if romName not in imgNameList:
            romListBox.itemconfig(tk.END, {'bg':'red'})
            noImageTextBox.insert(tk.INSERT, rom + "\n")
                        
    # set default value to first item
    romListBox.select_set(0)
    romListBox.event_generate("<<ListboxSelect>>")
    # show romListBox

# simple function for printing debug message
def debug(msg):
    debugLabel.configure(text=msg)

# event handler for romListBox
def romListBoxSelectHandler(event):
    romFile = romListBox.get(romListBox.curselection())
    import imgUtil
    imageTk = imgUtil.findImageFromRomName(romBox.get(), romFile)
    if (imageTk != None):        
        imgLabel.configure(image=imageTk)
        imgLabel.image = imageTk
        imgInfoLabel.configure(text="{}: {} X {}".format(romFile, imageTk.width(), imageTk.height()))
    else:
        imgLabel.configure(image=baseImageTk)
        imgInfoLabel.configure(text="Image Not Found") 


# 라벨들
label = ttk.Label(win, text="롬 폴더")
label.grid(column=0, row=0, pady=5, padx=5)

label2 = ttk.Label(win, text="불러온 롬 리스트")
label2.grid(column=0, row=2, pady=5, padx=5)

label3 = ttk.Label(win, text="이미지가 없는 롬들")
label3.grid(column=2, row=2, pady=5, padx=5)

label4 = ttk.Label(win, text="이미지 미리 보기")
label4.grid(column=0, row=4, pady=5, padx=5)

#load base Image
baseImageTk = ImageTk.PhotoImage(Image.open("images/base.png"))

imgLabel = ttk.Label(win, image=baseImageTk)
imgLabel.grid(column=0, row=5, pady=5, padx=5)

imgInfoLabel = ttk.Label(win, text="Image Info")
imgInfoLabel.grid(column=2, row=5, pady=5, padx=5)

# debug label
debugLabel = ttk.Label(win, text="debug")
debugLabel.grid(column=0, row=6, pady=5, padx=5)

# 폴더 선택 콤보 박스
romBox = ttk.Combobox(win, values=subdirs)
#set default value to first item
romBox.current(0)
romBox.grid(column=0, row=1, padx=5, pady=5)
romBox.bind("<<ComboboxSelected>>", listSelectedDir)

# 롬 리스트용 리스트 박스
from tkinter import Listbox
romListBox = Listbox(win)
romListBox.config(height=20, width= 50)
romListBox.bind('<<ListboxSelect>>', romListBoxSelectHandler)
romListBox.grid(column=0, row=3, padx=5, pady=5)


# 이미지가 없는 롬 목록 출력용
from tkinter import Text
noImageTextBox = Text(win)
noImageTextBox.config(height=20, width= 50)
noImageTextBox.grid(column=2, row=3, padx=5, pady=5)

romBox.event_generate("<<ComboboxSelected>>")

# 애플리케이션을 실행합니다.
win.mainloop()
