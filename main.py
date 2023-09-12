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
romBox.pack()

# add Button for selected romBox


# # rom list box 생성
# romListbox = tk.Listbox(win, height=20, width=50)


# # 롬 목록 선택시 이벤트 처리
# def romListSelected(*args):
#     print("romListSelected", numberChosen.get())
#     romList = [f for f in os.listdir(path.join('roms/', numberChosen.get())) if path.isfile(path.join('roms/', numberChosen.get(), f))]
#     romList.sort()
    
#     romListbox.delete(0, tk.END)
#     for rom in romList:
#         romListbox.insert(tk.END, rom)
#     romListbox.select_set(0)
#     romListbox.event_generate("<<ListboxSelect>>")  

# 애플리케이션을 실행합니다.
win.mainloop()
