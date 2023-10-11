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
from config import *
from xmlUtil import *
from fileUtil import *

# change working directory
os.chdir(ROM_PATH)

# global variable
xmlGameList = None
currentDir = os.getcwd()
targetDir = TARGET_PATH
# 마지막에 열었던 서브롬 폴더 이름
lastRom = LAST_ROM

# 마지막에 선택했던 롬파일 인덱스
lastRomIdx = 0
lastRomName = ""

# Create instance
root = tk.Tk()
root.title("RetroArch Rom Manager")
root.geometry("1200x900")

def subRomBoxHandler(event):
    '''
    롬 폴더 콤보 박스에서 폴더를 선택하면 해당 폴더의 롬 리스트를 보여준다.
    이미지가 없을 경우 빨간색으로 표시한다.
    없는 이미지는 가장 유사한 이미지 이름을 찾아서 보여준다.
    '''    
    global xmlGameList
    romDir = romBox.get()
    xmlGameList = XmlGameList(romDir)
    
    # 롬리스트박스와 메시지 박스를 초기화한다.
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

            # 이미지 디렉토리에서 가장 유사한 이미지를 찾아서 보여준다.
            similarImage = findSimilarImage(romDir, romName, path.dirname(game['image']))
            if similarImage != None:
                msgTextBox.insert(tk.INSERT, "가장 유사한 이미지 이름: {}\n\n".format(similarImage[0]))
            imgMissCount += 1
        else:
            imgFound += 1

    if imgMissCount == 0:
        msgTextBox.insert(tk.INSERT,"총 {}개의 롬의 모든 이미지가 정상적으로 존재합니다.".format(imgFound))
    else:           
        msgTextBox.insert(tk.INSERT,"\n총 {}개의 롬 중 {}개의 이미지가 존재하지 않습니다.".format(imgFound + imgMissCount, imgMissCount))

    # 첫 번째 롬을 선택하고 이벤트를 발생시켜 이미지를 미리 보여준다.
    global lastRomIdx
    if lastRomIdx >= romListBox.size():
        lastRomIdx = romListBox.size() - 1
    romListBox.select_set(lastRomIdx)
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

    global xmlGameList, lastRomIdx, lastRomName
    
    # 포커스를 잃을 경우 에러가 나는 문제 해결을 위한 코드
    if len(romListBox.curselection()) == 0: return

    lastRomIdx = romListBox.curselection()[0]
    lastRomName = romListBox.get(lastRomIdx)

    # 이미지를 미리 보여준다.
    import imgUtil
    romName = romListBox.get(romListBox.curselection())  
    iamgePath = xmlGameList.getImagePath(romName) 
    game = xmlGameList.findGame(romName)
    imageTk = imgUtil.findImage(romBox.get(), iamgePath)

    if len(iamgePath) > 20:
        iamgePath = iamgePath[:20] + "..."

    if (imageTk != None):        
        imgLabel.configure(image=imageTk)
        imgLabel.image = imageTk        
    else:
        imgLabel.configure(image=baseImageTk, width=500)    

    # 롬의 세부 정보를 보여준다.
    romTitleEntry.delete(0, tk.END)
    romTitleEntry.insert(0, game['name'])
    romPathEntry.delete(0, tk.END)
    romPathEntry.insert(0, game['path'])
    romImageEntry.delete(0, tk.END)
    romImageEntry.insert(0, game['image'])
    romDescriptionText.delete(1.0, tk.END)
    romDescriptionText.insert(1.0, game['desc'])

def deleteRomAndImageHandler():
    '''
    선택된 롬과 이미지를 삭제하는 핸들러
    '''

    # 먼저 파일과 이미지를 삭제한다.
    romName = romListBox.get(romListBox.curselection())
    romDir = romBox.get()

    deleteRomAndImages(romDir, xmlGameList.getRomPath(romName), xmlGameList.getImagePath(romName))

    # 롬리스트에서도 해당 목록을 제거한다.
    xmlGameList.remove(romName)
    
    # 롬 리스트를 다시 읽어서 보여준다.
    romBox.event_generate("<<ComboboxSelected>>")

########################
# 중첩 프레임          #
########################

# 타이틀 프레임
# 롬 선택 콤보 박스와 새로고침 버튼이 있는 프레임
titleFrame = ttk.Frame(root)
titleFrame.grid(column=1, row=0, pady=5, padx=5)

# 롬 리스트 프레임
romListFrame = ttk.Frame(root)
romListFrame.grid(column=0, row=1, pady=5, padx=5)

# 롬 세부 정보 프레임
detailedRomInfoFrame = ttk.Frame(root)
detailedRomInfoFrame.grid(column=1, row=1, pady=5, padx=5)

# 메시지용 프레임
outputMessageFrame = ttk.Frame(root)
outputMessageFrame.grid(column=0, row=2, pady=5, padx=5)

# 이미지 미리보기 프레임
imagePreviewFrame = ttk.Frame(root)
imagePreviewFrame.grid(column=1, row=2, pady=5, padx=5)

# 버튼 프레임
buttonFrame = ttk.Frame(root)
buttonFrame.grid(column=2, row=1, pady=5, padx=5, rowspan=2)

# 롬 폴더 선택 프레임
label = ttk.Label(titleFrame, text="롬 폴더")
label.grid(column=0, row=0, pady=5, padx=5)

# 폴더 선택 콤보 박스
romBox = ttk.Combobox(titleFrame, values=readSubDirs())
romBox.current(0)
romBox.grid(column=1, row=0, padx=5, pady=5)
romBox.bind("<<ComboboxSelected>>", subRomBoxHandler)

# 새로고침 버튼 
refreshButton = ttk.Button(titleFrame, text="새로고침", command=lambda: romBox.event_generate("<<ComboboxSelected>>"))
refreshButton.grid(column=2, row=0, pady=5, padx=5)

# 롬 리스트
label2 = ttk.Label(romListFrame, text="롬 리스트")
label2.grid(column=0, row=0, pady=5, padx=5)
from tkinter import Listbox
romListBox = Listbox(romListFrame)
romListBox.config(height=20, width= 60)
romListBox.bind('<<ListboxSelect>>', romListBoxSelectHandler)
romListBox.grid(column=0, row=1, padx=5, pady=5)

# 롬 세부 정보
romDescriptionLabel = ttk.Label(detailedRomInfoFrame, text="롬 세부 정보")
romDescriptionLabel.grid(column=0, row=0, pady=5, padx=5)

# 롬 제목
romTitleLabel = ttk.Label(detailedRomInfoFrame, text="롬 이름")
romTitleLabel.grid(column=0, row=1, pady=5, padx=5)
romTitleEntry = ttk.Entry(detailedRomInfoFrame, width=60)
romTitleEntry.grid(column=1, row=1, pady=5, padx=5) 

# 롬 경로
romPathLabel = ttk.Label(detailedRomInfoFrame, text="롬 경로")
romPathLabel.grid(column=0, row=2, pady=5, padx=5)
romPathEntry = ttk.Entry(detailedRomInfoFrame, width=60)
romPathEntry.grid(column=1, row=2, pady=5, padx=5)

# Rating
romRatingLabel = ttk.Label(detailedRomInfoFrame, text="Rating")
romRatingLabel.grid(column=0, row=3, pady=5, padx=5)
romRatingEntry = ttk.Entry(detailedRomInfoFrame, width=60)
romRatingEntry.grid(column=1, row=3, pady=5, padx=5)

# 이미지 경로
romImageLabel = ttk.Label(detailedRomInfoFrame, text="이미지 경로")
romImageLabel.grid(column=0, row=3, pady=5, padx=5)
romImageEntry = ttk.Entry(detailedRomInfoFrame, width=60)
romImageEntry.grid(column=1, row=3, pady=5, padx=5)

# 세부 정보
romDescriptionLabel = ttk.Label(detailedRomInfoFrame, text="세부 정보")
romDescriptionLabel.grid(column=0, row=4, pady=5, padx=5)
romDescriptionText = scrolledtext.ScrolledText(detailedRomInfoFrame, width=60, height=10)
romDescriptionText.grid(column=1, row=4, pady=5, padx=5)

# 롬 정보 업데이트 버튼
def updateRomInfoHandler():
    '''
    롬 정보를 업데이트하는 핸들러
    '''
    global xmlGameList, lastRomName

    # 롬 선택 핸들러 코드를 참고할 것 
    # 롬 정보를 수정하면 롬리스트가 포커스를 잃어버리기 때문에 미리 lastRomName을 저장해 두었다.    
    game = xmlGameList.findGame(lastRomName)
    
    # 새로운 다이얼로그를 열어 정말 저장 할 건지 물어본다.
    romInfo = '''롬 이름: {}
    롬 경로: {}
    롬 Rating: {}
    이미지 경로: {}    
    세부 정보: {}'''.format(romTitleEntry.get(), romPathEntry.get(), romRatingEntry.get(), romImageEntry.get(), romDescriptionText.get(1.0, tk.END))
    result = mBox.askquestion("롬 정보 업데이트", "{} 롬 정보를 업데이트 하시겠습니까?".format(romInfo))
    if result == 'yes':
        game['name'] = romTitleEntry.get()
        game['path'] = romPathEntry.get()
        game['image'] = romImageEntry.get()
        game['desc'] = romDescriptionText.get(1.0, tk.END)
        xmlGameList.updateGame(lastRomName, game)
        romBox.event_generate("<<ComboboxSelected>>")
        

romUpdateButton = ttk.Button(detailedRomInfoFrame, text="롬 정보 업데이트", command=updateRomInfoHandler)
romUpdateButton.grid(column=1, row=5, pady=5, padx=5)



# 롬 세부 정보

# 출력 메시지
label3 = ttk.Label(outputMessageFrame, text="출력 메시지")
label3.grid(column=0, row=0, pady=5, padx=5)
# 메시지 출력용 텍스트 박스
msgTextBox = Text(outputMessageFrame)
msgTextBox.config(height=30, width= 60)
msgTextBox.grid(column=0, row=1, padx=5, pady=5)


# 이미지 미리보기
label4 = ttk.Label(imagePreviewFrame, text="이미지 미리 보기")
label4.grid(column=0, row=0, pady=5, padx=5)
# 포토 이미지 라벨
baseImageTk = ImageTk.PhotoImage(Image.open(BASE_IMAGE))
imgLabel = ttk.Label(imagePreviewFrame, image=baseImageTk)
imgLabel.grid(column=0, row=1, pady=5, padx=5)

# debug label
debugLabel = ttk.Label(root, text="debug")
debugLabel.grid(column=0, row=3, columnspan=2, pady=5, padx=5)

#######################################
# buttons                             #
#######################################

# 폴더 찾기 버튼
folderSelectButton = ttk.Button(buttonFrame, text="대상 폴더 열기", command=lambda: os.startfile(targetDir))
folderSelectButton.grid(column=0, row=0, pady=5, padx=5)

# 롬 폴더 열기 버튼
romFolderOpenButton = ttk.Button(buttonFrame, text="롬 폴더 열기", command=lambda: os.startfile(romBox.get()))
romFolderOpenButton.grid(column=0, row=1, pady=5, padx=5)

# 이미지 폴더 열기 버튼
imgFolderOpenButton = ttk.Button(buttonFrame, text="이미지 폴더 열기", command=lambda: os.startfile(path.join(romBox.get(),'box')))
imgFolderOpenButton.grid(column=0, row=2, pady=5, padx=5)

# 롬 파일 및 이미지 삭제 버튼
fileDeleteButton = ttk.Button(buttonFrame, text="선택 롬/이미지 삭제", command=deleteRomAndImageHandler)
fileDeleteButton.grid(column=0, row=3, pady=5, padx=5)

# 마지막으로 선택된 폴더의 롬 리스트를 보여줌
if lastRom in romBox['values']:
    romBox.set(lastRom)
romBox.event_generate("<<ComboboxSelected>>")

# 애플리케이션을 실행합니다.
ico = Image.open(ICON)
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
root.mainloop()
