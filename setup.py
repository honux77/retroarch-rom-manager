'''
환경 설정을 위한 모달 창을 정의
'''

# Import: built-in
import os
import sys

import tkinter as tk
from tkinter import ttk

from config import Config


def openSetupWindow(root):
    '''
    환경 설정 창을 열고 환경 설정 값을 변경한다.
    '''    
    setupWindow = tk.Toplevel(root)
    setupWindow.title('환경 설정')
    setupWindow.geometry('400x300')

    config = Config()

    setupWindow.grab_set()


    # 프레임 생성
    frame = ttk.Frame(setupWindow)
    frame.pack(fill=tk.BOTH, expand=True)

    # 기본 경로
    basePathLabel = ttk.Label(frame, text='기본 경로')
    basePathLabel.grid(row=0, column=0, sticky=tk.W)
    basePathEntry = ttk.Entry(frame, width=50)
    basePathEntry.insert(0, config.getBasePath())

    # 대상 경로
    targetPathLabel = ttk.Label(frame, text='대상 경로')
    targetPathLabel.grid(row=1, column=0, sticky=tk.W)
    targetPathEntry = ttk.Entry(frame, width=50)
    targetPathEntry.insert(0, config.getTargetPath())
    

    
