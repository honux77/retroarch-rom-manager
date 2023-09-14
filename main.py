# simple gui apllication
import os
from os import path

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as mBox
from tkinter import Text

from PIL import ImageTk, Image

import fileUtil
import filenameUtil
import imgUtil

# for global variable
from config import *

# Create instance
win = tk.Tk()

# Add a title
win.title("Famliy Pocket Rom Manager")


# roms 폴더의 서브 폴더들을 읽어서 드롭리스트에 추가
def readSubDirs():        
    subdirs = [f for f in os.listdir('roms/') if path.isdir(path.join('roms/', f))]
    return subdirs

# Set size of window
win.geometry("1100x800")

# event handler for select_button
def listSelectedDir(event):
    dir = romBox.get()
    import fileUtil
    romList = fileUtil.getRomList(dir)
    
    # get image list and cut extension
    imgNameList = [path.splitext(f)[0] for f in fileUtil.getImgList(dir)]
    
    # delete romListBox
    romListBox.delete(0, tk.END)    

    #delete msgTextBox
    msgTextBox.delete(1.0, tk.END)
    msgTextBox.insert(tk.INSERT, "=== 존재하지 않는 이미지 목록 ===\n\n")

    found = 0
    notFound = 0

    for rom in romList:
        romName = path.splitext(rom)[0]
        romListBox.insert(tk.END, rom)                    
        
        if romName not in imgNameList:
            romListBox.itemconfig(tk.END, {'bg':'red'})
            msgTextBox.insert(tk.INSERT, romName + ".png\n")
            notFound += 1
        else:
            found += 1
                        
    msgTextBox.insert(tk.INSERT,"\n총 {}개의 롬 중 {}개의 이미지가 존재하지 않습니다.".format(found + notFound, notFound))

    # 첫번째 롬을 선택하고 이벤트를 발생시켜서 이미지 미리 보기를 실행
    romListBox.select_set(0)
    romListBox.event_generate("<<ListboxSelect>>")
    

# simple function for printing debug message
def debug(msg):
    debugLabel.configure(text=msg)

# event handler for romListBox
# 롬 선택시 이미지 미리 보기 실행
def romListBoxSelectHandler(event):
    romFile = romListBox.get(romListBox.curselection())
    import imgUtil
    imageName = path.splitext(romFile)[0] + '.png'
    imageTk = imgUtil.findImage(romBox.get(), imageName)
    if (imageTk != None):        
        imgLabel.configure(image=imageTk)
        imgLabel.image = imageTk
        debug("{}: {} X {} ".format(imageName, imageTk.width(), imageTk.height()))
    else:
        imgLabel.configure(image=baseImageTk)
        debug("{} Not Found".format(imageName))

# 다겟 티렉토리 지정
def selectDir():
    global targetDir
    import openDir    
    print(targetDir)
    dir = openDir.openFileDialog(currentDir=targetDir)    
    if dir != None:               
        if path.isdir(path.join(dir, 'roms')) and path.isdir(path.join(dir, 'images')):
             targetDir = dir
             debug("타겟 디렉토리 변경: " +targetDir)
        else:
            debug("디렉토리 변경 실패")    

# 롬 파일 및 이미지 삭제 이벤트 핸들러
def deleteRomAndImages():
    romName = romListBox.get(romListBox.curselection())
    subPath = romBox.get()
    fileUtil.deleteRomAndImages(subPath, romName)
    romBox.event_generate("<<ComboboxSelected>>")

# 이미지 크롭 및 리사이즈 핸들러
def resizeAllImages():
    import imageCrop
    subPath = romBox.get()
    n = imageCrop.resizeAndCropAll(subPath, msgTextBox)
    debug("{} 이미지 리사이즈 완료".format(n))

# 롬 이름 단순화 핸들러
def simplifyRomName():
    subPath = romBox.get()
    msgTextBox.delete(1.0, tk.END)
    msgTextBox.insert(tk.INSERT, "=== 롬 이름 단순화 시작 ===\n")    
    n = filenameUtil.simplifyRomName(subPath, msgTextBox)
    msgTextBox.insert(tk.INSERT, "\n{} 롬 이름 단순화 완료\n".format(n))
    debug("{} 롬 이름 단순화 완료".format(n)) 
    

# 이미지 이름 단순화 핸들러
def simplifyImageName():
    subPath = romBox.get()
    msgTextBox.delete(1.0, tk.END)
    msgTextBox.insert(tk.INSERT, "=== 이미지 이름 단순화 시작 ===\n")    
    n = filenameUtil.simplifyImageName(subPath, msgTextBox)
    msgTextBox.insert(tk.INSERT, "\n{} 이미지 이름 단순화 완료\n".format(n))
    debug("{} 이미지 이름 단순화 완료".format(n))

########################
# 라벨들               #
########################

label = ttk.Label(win, text="롬 폴더")
label.grid(column=0, row=0, pady=5, padx=5)

label2 = ttk.Label(win, text="불러온 롬 리스트")
label2.grid(column=0, row=2, pady=5, padx=5)

label3 = ttk.Label(win, text="출력 메시지")
label3.grid(column=2, row=2, pady=5, padx=5)

label4 = ttk.Label(win, text="이미지 미리 보기")
label4.grid(column=0, row=4, pady=5, padx=5)

#baseImage and imgLabel
baseImageTk = ImageTk.PhotoImage(Image.open("images/base.png"))
imgLabel = ttk.Label(win, image=baseImageTk)
imgLabel.grid(column=0, row=5, pady=5, padx=5)

# debug label
debugLabel = ttk.Label(win, text="debug")
debugLabel.grid(column=0, row=6, pady=5, padx=5)

#######################################
# buttons                             #
#######################################

# 폴더 찾기 버튼
folderSelectButton = ttk.Button(win, text="대상 폴더 지정", command=selectDir)
folderSelectButton.grid(column=3, row=0, pady=5, padx=5)

# 이미지 리사이즈 버튼
imageResizeButton = ttk.Button(win, text="이미지 리사이즈", command=resizeAllImages)
imageResizeButton.grid(column=4, row=0, pady=5, padx=5)

# 롬 이름 단순화 버튼
romNameSimplifyButton = ttk.Button(win, text="롬 이름 단순화", command=simplifyRomName)
romNameSimplifyButton.grid(column=3, row=1, pady=5, padx=5)

# 이미지 이름 단순화 버튼
romNameSimplifyButton = ttk.Button(win, text="이미지 이름 단순화", command=simplifyImageName)
romNameSimplifyButton.grid(column=4, row=1, pady=5, padx=5)

# 롬 파일 및 이미지 삭제 버튼
fileDeleteButton = ttk.Button(win, text="선택 롬/이미지 삭제", command=deleteRomAndImages)
fileDeleteButton.grid(column=3, row=3, pady=5, padx=5)


#######################################
# comboboxes                          #
#######################################

# 폴더 선택 콤보 박스
romBox = ttk.Combobox(win, values=readSubDirs())
#set default value to first item
romBox.current(0)
romBox.grid(column=0, row=1, padx=5, pady=5)
romBox.bind("<<ComboboxSelected>>", listSelectedDir)


#######################################
# listboxes                           #
#######################################

# 롬 리스트용 리스트 박스
from tkinter import Listbox
romListBox = Listbox(win)
romListBox.config(height=20, width= 40)
# 롬 선택시 이미지 미리 보기
romListBox.bind('<<ListboxSelect>>', romListBoxSelectHandler)
romListBox.grid(column=0, row=3, padx=5, pady=5)

#######################################
# textboxes                           #
#######################################

# 메시지 출력용 텍스트 박스
msgTextBox = Text(win)
msgTextBox.config(height=25, width= 70)
msgTextBox.grid(column=2, row=3, padx=5, pady=5)

# 마지막으로 최초 선택된 폴더의 롬 리스트를 보여줌
romBox.event_generate("<<ComboboxSelected>>")

# 애플리케이션을 실행합니다.
ico = Image.open('icon16.png')
photo = ImageTk.PhotoImage(ico)
win.wm_iconphoto(False, photo)
win.mainloop()
