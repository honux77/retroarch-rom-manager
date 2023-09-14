# simple gui apllication
import os
from os import path

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as mBox
from tkinter import Text
from tkinter import simpledialog

from PIL import ImageTk, Image

import fileUtil
import filenameUtil
import imgUtil

# for global variable
from config import *

# Create instance
root = tk.Tk()
root.title("Famliy Pocket Rom Manager")
root.geometry("900x800")



# roms 폴더의 서브 폴더들을 읽어서 드롭리스트에 추가
# TODO: 별도 분리할 것
def readSubDirs():        
    subdirs = [f for f in os.listdir('roms/') if path.isdir(path.join('roms/', f))]
    return subdirs
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

    found = 0
    notFound = 0

    for rom in romList:
        romName = path.splitext(rom)[0]
        romListBox.insert(tk.END, rom)                    
        
        if romName not in imgNameList:
            if found == 0:
                msgTextBox.insert(tk.INSERT, "=== 존재하지 않는 이미지 목록 ===\n\n")

            romListBox.itemconfig(tk.END, {'bg':'red'})
            msgTextBox.insert(tk.INSERT, romName + ".png\n")      

            # 유사한 이름을 추천해 줌
            similarImage = fileUtil.findSimilarImage(romName, imgNameList)
            msgTextBox.insert(tk.INSERT, "가장 유사한 이미지 이름: {}.png\n\n".format(similarImage[0]))
            notFound += 1

        else:
            found += 1

    if notFound == 0:
        msgTextBox.insert(tk.INSERT,"총 {}개의 롬의 모든 이미지가 정상적으로 존재합니다.".format(found))
    else:           

        msgTextBox.insert(tk.INSERT,"\n총 {}개의 롬 중 {}개의 이미지가 존재하지 않습니다.".format(found + notFound, notFound))

    # 첫번째 롬을 선택하고 이벤트를 발생시켜서 이미지 미리 보기를 실행
    romListBox.select_set(0)
    romListBox.event_generate("<<ListboxSelect>>")
    

def debug(msg):
    '''
    디버그 메시지를 디버깅용 라벨에 출력한다.
    msg: 출력할 메시지
    '''
    debugLabel.configure(text=msg)

def romListBoxSelectHandler(event):
    '''
    롬 선택시 이미지 미리 보기를 실행하는 핸들러
    event: tkinter의 이벤트 객체
    '''
    
    # 포커스를 잃을 경우 에러가 나는 문제 해결을 위한 코드
    if len(romListBox.curselection()) == 0: return
    
    romFile = romListBox.get(romListBox.curselection())
    import imgUtil
    imageName = path.splitext(romFile)[0] + '.png'    
    imageTk = imgUtil.findImage(romBox.get(), imageName)

    if len(imageName) > 20:
        imageName = imageName[:20] + "..."

    if (imageTk != None):        
        imgLabel.configure(image=imageTk)
        imgLabel.image = imageTk
        imgInfoLabel.configure(text="{} X {} ".format(imageTk.width(), imageTk.height()))
    else:
        imgLabel.configure(image=baseImageTk)
        imgInfoLabel.configure(text="{} Not Found".format(imageName))        

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

# 롬 및 이미지 이름 변경 핸들러
def renameRomAndImages():
    oldName = path.splitext(romListBox.get(romListBox.curselection()))[0]
    # show input dialog
    newName = simpledialog.askstring("롬 이름 변경", "변경할 롬 이름을 입력하세요", initialvalue=oldName)

    if newName == None or newName == "" or newName == oldName:
        debug("롬 이름 변경 취소")
        return
        
    filenameUtil.renameRomAndImages(romBox.get(), oldName, newName)
    debug("롬 이름 변경 완료")
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
# 중첩 프레임          #
########################

titleFrame = ttk.Frame(root)
titleFrame.grid(column=1, row=0, pady=5, padx=5)

romListFrame = ttk.Frame(root)
romListFrame.grid(column=0, row=1, pady=5, padx=5)

outputMessageFrame = ttk.Frame(root)
outputMessageFrame.grid(column=1, row=1, pady=5, padx=5)

imagePreviewFrame = ttk.Frame(root)
imagePreviewFrame.grid(column=0, row=2, pady=5, padx=5)

buttonFrame = ttk.Frame(root)
buttonFrame.grid(column=1, row=2, pady=5, padx=5)

# 롬 폴더 선택 프레임

label = ttk.Label(titleFrame, text="롬 폴더")
label.grid(column=0, row=0, pady=5, padx=5)

# 폴더 선택 콤보 박스
romBox = ttk.Combobox(titleFrame, values=readSubDirs())
romBox.current(0)
romBox.grid(column=1, row=0, padx=5, pady=5)
romBox.bind("<<ComboboxSelected>>", listSelectedDir)

# 새로고침 버튼 
refreshButton = ttk.Button(titleFrame, text="새로고침", command=lambda: romBox.event_generate("<<ComboboxSelected>>"))
refreshButton.grid(column=2, row=0, pady=5, padx=5)

# 롬 리스트
label2 = ttk.Label(romListFrame, text="롬 리스트")
label2.grid(column=0, row=0, pady=5, padx=5)
from tkinter import Listbox
romListBox = Listbox(romListFrame)
romListBox.config(height=20, width= 50)
romListBox.bind('<<ListboxSelect>>', romListBoxSelectHandler)
romListBox.grid(column=0, row=1, padx=5, pady=5)


# 출력 메시지
label3 = ttk.Label(outputMessageFrame, text="출력 메시지")
label3.grid(column=0, row=0, pady=5, padx=5)
# 메시지 출력용 텍스트 박스
msgTextBox = Text(outputMessageFrame)
msgTextBox.config(height=25, width= 70)
msgTextBox.grid(column=0, row=1, padx=5, pady=5)


# 이미지 미리보기
label4 = ttk.Label(imagePreviewFrame, text="이미지 미리 보기")
label4.grid(column=0, row=0, pady=5, padx=5)
# 이미지 표시용 라벨
baseImageTk = ImageTk.PhotoImage(Image.open("images/base.png"))
imgLabel = ttk.Label(imagePreviewFrame, image=baseImageTk)
imgLabel.grid(column=0, row=1, pady=5, padx=5)
# 이미지 정보표시 라벨
imgInfoLabel = ttk.Label(imagePreviewFrame, text="이미지 정보")
imgInfoLabel.grid(column=0, row=2, pady=5, padx=5)


# debug label
debugLabel = ttk.Label(root, text="debug")
debugLabel.grid(column=0, row=3, columnspan=2, pady=5, padx=5)

#######################################
# buttons                             #
#######################################

# 폴더 찾기 버튼
folderSelectButton = ttk.Button(buttonFrame, text="대상 폴더 지정", command=selectDir)
folderSelectButton.grid(column=0, row=0, pady=5, padx=5)

# 폴더 찾기 버튼
folderSelectButton = ttk.Button(buttonFrame, text="대상 폴더 열기", command=lambda: os.startfile(targetDir))
folderSelectButton.grid(column=1, row=0, pady=5, padx=5)

# 이미지 리사이즈 버튼
imageResizeButton = ttk.Button(buttonFrame, text="이미지 리사이즈", command=resizeAllImages)
imageResizeButton.grid(column=2, row=0, pady=5, padx=5)

# 롬 이름 단순화 버튼
romNameSimplifyButton = ttk.Button(buttonFrame, text="롬 이름 단순화", command=simplifyRomName)
romNameSimplifyButton.grid(column=0, row=1, pady=5, padx=5)

# 이미지 이름 단순화 버튼
romNameSimplifyButton = ttk.Button(buttonFrame, text="이미지 이름 단순화", command=simplifyImageName)
romNameSimplifyButton.grid(column=1, row=1, pady=5, padx=5)


# 롬 폴더 열기 버튼
romFolderOpenButton = ttk.Button(buttonFrame, text="롬 폴더 열기", command=lambda: os.startfile(path.join('roms', romBox.get())))
romFolderOpenButton.grid(column=0, row=2, pady=5, padx=5)

# 이미지 폴더 열기 버튼
imgFolderOpenButton = ttk.Button(buttonFrame, text="이미지 폴더 열기", command=lambda: os.startfile(path.join('images', romBox.get())))
imgFolderOpenButton.grid(column=1, row=2, pady=5, padx=5)

# 롬 파일 및 이미지 삭제 버튼
fileDeleteButton = ttk.Button(buttonFrame, text="선택 롬/이미지 삭제", command=deleteRomAndImages)
fileDeleteButton.grid(column=0, row=3, pady=5, padx=5)

# 롬 파일 및 이미지 이름 변경
fileDeleteButton = ttk.Button(buttonFrame, text="선택 롬/이미지 이름변경", command=renameRomAndImages)
fileDeleteButton.grid(column=1, row=3, pady=5, padx=5)

# 마지막으로 최초 선택된 폴더의 롬 리스트를 보여줌
romBox.event_generate("<<ComboboxSelected>>")

# 애플리케이션을 실행합니다.
ico = Image.open('icon16.png')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
root.mainloop()
