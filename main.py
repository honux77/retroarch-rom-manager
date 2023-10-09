# simple gui apllication
import os
from os import path

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import Text
from tkinter import simpledialog

from PIL import ImageTk, Image

# local module
import config
import xmlUtil
import fileUtil

# change working directory
os.chdir(config.ROM_PATH)

# global variable
xmlGameList = None
currentDir = os.getcwd()

# Create instance
root = tk.Tk()
root.title("RetroArch Rom Manager")
root.geometry("900x800")


def readSubDirs():        
    '''
    roms 폴더의 하위 폴더를 읽어서 리스트로 반환한다.
    바이오스 폴더는 제외한다.
    '''
    return [f for f in os.listdir() if path.isdir(f) and f != 'bios']

def listSelectedDir(event):
    '''
    콤보 박스에서 폴더를 선택하면 해당 폴더의 롬 리스트를 보여준다.
    이미지가 없을 경우 빨간색으로 표시한다.
    '''
    global xmlGameList
    romDir = romBox.get()
    xmlGameList = xmlUtil.XmlGameList(romDir)
    
    # delete romListBox and msgTextBox
    romListBox.delete(0, tk.END)        
    msgTextBox.delete(1.0, tk.END)
    
    imgFound = 0
    imgMissCount = 0

    for game in xmlGameList.gameList:
        romName = game['name']
        romListBox.insert(tk.END, romName)                    
        
        if not os.path.isfile(path.join(romDir, game['image'])):
            if imgMissCount == 0: msgTextBox.insert(tk.INSERT, "=== 존재하지 않는 이미지 목록 ===\n\n")

            romListBox.itemconfig(tk.END, {'bg':'red'})
            msgTextBox.insert(tk.INSERT, game['image'] + "\n")      

            # 유사한 이름을 추천해 줌
            similarImage = fileUtil.findSimilarImage(romDir, romName, "box")
            msgTextBox.insert(tk.INSERT, "가장 유사한 이미지 이름: {}.png\n\n".format(similarImage[0]))
            imgMissCount += 1
        else:
            imgFound += 1

    if imgMissCount == 0:
        msgTextBox.insert(tk.INSERT,"총 {}개의 롬의 모든 이미지가 정상적으로 존재합니다.".format(imgFound))
    else:           
        msgTextBox.insert(tk.INSERT,"\n총 {}개의 롬 중 {}개의 이미지가 존재하지 않습니다.".format(imgFound + imgMissCount, imgMissCount))

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

    global xmlGameList
    
    # 포커스를 잃을 경우 에러가 나는 문제 해결을 위한 코드
    if len(romListBox.curselection()) == 0: return

    import imgUtil
    romFile = romListBox.get(romListBox.curselection())  
    iamgePath = xmlGameList.getImagePath(romFile) 
    imageTk = imgUtil.findImage(romBox.get(), iamgePath)

    if len(iamgePath) > 20:
        iamgePath = iamgePath[:20] + "..."

    if (imageTk != None):        
        imgLabel.configure(image=imageTk)
        imgLabel.image = imageTk
        imgInfoLabel.configure(text="{} X {} ".format(imageTk.width(), imageTk.height()))
    else:
        imgLabel.configure(image=baseImageTk, width=500)
        imgInfoLabel.configure(text="{} Not Found".format(iamgePath))        

def selectDir():
    '''
    openFile 다이얼로그를 열어 타겟 디렉토리를 지정한다.
    '''
    global targetDir
    import openDir    
    print(targetDir)
    dir = openDir.openFileDialog(currentDir=targetDir)    
    if dir != None:               
        if path.isdir(dir):
             targetDir = dir
             debug("타겟 디렉토리 변경: " +targetDir)
        else:
            debug("디렉토리 변경 실패")    


def deleteRomAndImageHandler():
    '''
    선택된 롬과 이미지를 삭제하는 핸들러
    '''

    # 먼저 파일과 이미지를 삭제한다.
    romName = romListBox.get(romListBox.curselection())
    romDir = romBox.get()
    fileUtil.deleteRomAndImages(romDir, romName, xmlGameList.getImagePath(romName))

    # 롬리스트에서도 해당 목록을 제거한다.
    xmlGameList.remove(romName)
    
    # 롬 리스트를 다시 읽어서 보여준다.
    romBox.event_generate("<<ComboboxSelected>>")

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
baseImageTk = ImageTk.PhotoImage(Image.open(config.BASE_IMAGE))
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

# 롬 폴더 열기 버튼
romFolderOpenButton = ttk.Button(buttonFrame, text="롬 폴더 열기", command=lambda: os.startfile(path.join('roms', romBox.get())))
romFolderOpenButton.grid(column=0, row=2, pady=5, padx=5)

# 이미지 폴더 열기 버튼
imgFolderOpenButton = ttk.Button(buttonFrame, text="이미지 폴더 열기", command=lambda: os.startfile(path.join(romBox.get(),'box')))
imgFolderOpenButton.grid(column=1, row=2, pady=5, padx=5)

# 롬 파일 및 이미지 삭제 버튼
fileDeleteButton = ttk.Button(buttonFrame, text="선택 롬/이미지 삭제", command=deleteRomAndImageHandler)
fileDeleteButton.grid(column=0, row=3, pady=5, padx=5)

# 마지막으로 최초 선택된 폴더의 롬 리스트를 보여줌
romBox.event_generate("<<ComboboxSelected>>")

# 애플리케이션을 실행합니다.
ico = Image.open(config.ICON)
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
root.mainloop()
