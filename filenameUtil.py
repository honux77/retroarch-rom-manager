import os
from os import path
import re
import tkinter as tk
from tkinter import messagebox as mBox

from config import ROM_PATH, IMAGE_PATH, EXT

def simplifyImageName(subRomDir, msgTextBox:tk.Text):
    '''
    이미지 파일명을 간단하게 변경한다.
    subRomDir: 이미지 파일이 있는 폴더명
    msgTextBox: 메시지를 출력할 텍스트 박스
    '''    
    return _simplifyFileName(IMAGE_PATH, subRomDir, '.png', msgTextBox)


def simplifyRomName(subRomDir, msgTextBox:tk.Text):
    '''
    롬 파일명을 간단하게 변경한다.
    subRomDir: 이미지 파일이 있는 폴더명
    msgTextBox: 메시지를 출력할 텍스트 박스
    '''
    return _simplifyFileName(ROM_PATH, subRomDir, EXT[subRomDir], msgTextBox)   
    
def renameRomAndImages(subPath, oldName, newName):
    '''
    롬 파일명과 이미지 파일명을 변경한다.
    subPath: 롬 파일이 있는 서브 폴더명
    romName: 변경할 롬 파일명
    newName: 새롭게 변경할 롬 파일명
    '''
    oldRom = path.join(ROM_PATH, subPath, oldName + EXT[subPath])
    newRom = path.join(ROM_PATH, subPath, newName + EXT[subPath])
    os.rename(oldRom, newRom)
            
    oldImg = path.join(IMAGE_PATH, subPath, oldName + '.png')
    newImg = path.join(IMAGE_PATH, subPath, newName + '.png')
    os.rename(oldImg, newImg)


def _simplifyFileName(basePath, subDir, extension, msgTextBox:tk.Text):
    '''
    simplifyXXX 메소드의 공통 사용 부분 함수로 분리한 프라이빗 메소드
    subDir: 파일이 있는 서브 폴더명
    extension: 대상 파일 확장자
    msgTextBox: 메시지를 출력할 텍스트 박스
    '''
    currPath = os.getcwd()
    
    os.chdir(path.join(basePath, subDir))    
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(extension)]

    count = 0    
    for f in files:
        f2 = os.path.splitext(f)[0]        
        # 괄호 및 대괄호로 둘러싸인 문자열 제거
        f2 = re.sub(r'\[.*?\]', '', f2)
        f2 = re.sub(r'\(.*?\)', '', f2)
        # 마지막에 있는 .과 공백 제거, 반복적으로 수행됨
        f2 = f2.rstrip(". ") + extension              
        
        if (f2 == f):             
            continue
        
        if (os.path.exists(f2)):
            os.remove(f2)
            msgTextBox.insert(tk.INSERT, "존재하는 파일 삭제: {}\n".format(f2))            

        os.rename(f, f2)
        msgTextBox.insert(tk.INSERT, "[{}] --> [{}]\n".format(f, f2))        
        count += 1        

    os.chdir(currPath)
    return count    