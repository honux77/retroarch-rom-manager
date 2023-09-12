# simple gui apllication

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as mBox

# Create instance
win = tk.Tk()

# Add a title
win.title("Famliy Pocket Rom Manager")

# Set size of window
win.geometry("1024x768")

# Add close button
def _quit():
    win.quit()
    win.destroy()
    exit()



# 롬 목록 드롭리스트 추가
label = ttk.Label(win, text="롬 목록 선택")
label.pack()

# roms 폴더의 서브 폴더들을 읽어서 드롭리스트에 추가
import os
from os import path
subdirs = [f for f in os.listdir('roms/') if path.isdir(path.join('roms/', f))]

romBox = ttk.Combobox(win, values=subdirs)
#set default value to first item
romBox.current(0)
romBox.pack()

# add Button for selected romBox
def listSelectedDir():
    dir = romBox.get()
    import fileUtil
    romList = fileUtil.getRomList(dir)
    
    # get image list and cut extension
    imgNameList = [path.splitext(f)[0] for f in fileUtil.getImgList(dir)]
    
    # add romList to romListBox
    romListBox.delete(0, tk.END)    

    for rom in romList:
        romName = path.splitext(rom)[0]
        romListBox.insert(tk.END, rom)            
        noImgList = ""
        
        if romName not in imgNameList:
            romListBox.itemconfig(tk.END, {'bg':'red'})
            noImgList += rom + "\n"

        
    # resize romListBox
    romListBox.config(height=len(romList), width= 50)
    # set default value to first item
    romListBox.select_set(0)
    # show romListBox
    romListBox.pack()

    # add no image list to scrolledtext
    noImageTextBox.delete(1.0, tk.END)
    noImageTextBox.insert(tk.INSERT, noImgList)
    noImageTextBox.pack()
    


    

# 선택 버튼을 추가하고 이 버튼을 클릭하면 선택된 항목을 표시하는 함수를 호출합니다.
select_button = ttk.Button(win, text="선택", command=listSelectedDir)
select_button.pack()

# 선택 결과를 표시할 listBox 추가
from tkinter import Listbox
romListBox = Listbox(win)
# hide romListBox
romListBox.pack_forget()


# 이미지가 없는 롬 목록 출력용
from tkinter import Text
noImageTextBox = Text(win)
noImageTextBox.pack_forget()

# 애플리케이션을 실행합니다.
win.mainloop()
