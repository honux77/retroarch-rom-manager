'''
롬 리스트를 정리하는 스크립트
1. 리스트에만 있고 실제 파일이 없을 경우 해당 파일 제거
2. 필수 속성이 없을 경우 필수 속성 추가
'''

import os
from os import path
import xml.etree.ElementTree as ET

import config
basePath = config.ROM_PATH
ext = config.EXT
xmlList = config.XML_LIST

os.chdir(basePath)


def removeGame(games, subRomDir):
    for game in games:
        if not path.isfile(path.join(subRomDir, game.find('path').text)):
            print(game.find('name').text, "is missing.")
            games.remove(game)
            return True
    return False


def cleanList(subRomDir):
    '''
    롬 리스트에서 실제 파일이 없는 항목을 제거한다.
    '''
    from os import path
    tree = ET.parse(path.join(subRomDir, xmlList))
    games = tree.getroot()
    n = len(games)
    print(subRomDir, "Total games: ", n)
    miss = 0
    while removeGame(games, subRomDir):
        miss += 1    
    print("Missing games: ", miss)     
    tree.write(path.join(subRomDir, xmlList), 'UTF-8')
    

def addGame(subRomDir):
    '''
    롬 리스트에 실제 파일이 있는 항목을 추가한다.
    '''
    from os import path

    print("Add game in ", subRomDir)

    files = [f for f in os.listdir(subRomDir) if path.isfile(path.join(subRomDir, f)) and f[-3:] in ext]    

    tree = ET.parse(path.join(subRomDir, xmlList))
    games = tree.getroot()
    gamePaths = [game.find('path').text[2:] for game in games]

    for file in files:
        if file not in gamePaths:            
            game = ET.SubElement(games, 'game')
            name = ET.SubElement(game, 'name')
            name.text = file[:-4]
            name.tail = '\n\t\t'
            gpath = ET.SubElement(game, 'path')
            gpath.text = "./" + file
            gpath.tail = '\n\t\t'
            image = ET.SubElement(game, 'image')
            image.text = "./box/" + file[:-4] + ".png"
            image.tail = '\n\t\t'
            rating = ET.SubElement(game, 'rating')
            rating.text = '0.6'
            rating.tail = '\n\t\t'
            game.tail = '\n\t'
            print(file, "is added.")     
    tree.write(path.join(subRomDir, xmlList), 'UTF-8')   

def addProperties(subRomDir):
    '''
    롬 리스트에 필수 속성이 없을 경우 추가한다.
    필수 속성: rating, image
    '''
    from os import path
    tree = ET.parse(path.join(subRomDir, xmlList))
    games = tree.getroot()
    for game in games:

        # 경로가 ./로 시작하지 않으면 ./를 추가한다.
        if game.find('path').text[:2] != './':
            game.find('path').text = './' + game.find('path').text
            game.find('path').tail = '\n\t\t'

        if game.find('rating') is None:
            rating = ET.SubElement(game, 'rating')
            rating.text = '0.6'
            rating.tail = '\n\t\t'
            
        if game.find('image') is None:
            image = ET.SubElement(game, 'image')
            # get filename without extension
            fileName = path.splitext(game.find('path').text)[0][2:]
            image.text =  "./box/" + fileName + ".png"
            image.tail = '\n\t\t'
        
        # images 경로가 box가 아닌 경우 box로 변경한다.
        if game.find('image').text[:7] != './box/':
            game.find('image').text = './box/' + path.basename(game.find('image').text)
            game.find('image').tail = '\n\t\t'
    tree.write(path.join(subRomDir, xmlList), 'UTF-8')

def changeTitleToKorean(subRomDir):
    '''
    리스트의 타이틀이 영문인 경우 한글로 변경한다.
    '''
    from os import path
    tree = ET.parse(path.join(subRomDir, xmlList))
    games = tree.getroot()
    for game in games:
        if game.find('name').text.isascii():
            print("영문 타이틀을 찾았습니다.", game.find('name').text, game.find('path').text)
            newTilte = input("새로운 한글 제목을 입력하세요: (엔터 입력시 변경하지 않음)")
            if newTilte != "":
                game.find('name').text = newTilte
                print("변경되었습니다.", game.find('name').text)
    tree.write(path.join(subRomDir, xmlList), 'UTF-8')



subDirs = [f for f in os.listdir('.') if os.path.isdir(f) and f != 'bios']

# for dir in subDirs:
#     cleanList(dir)    
#     addProperties(dir)
#     addGame(dir)
#     changeTitleToKorean(dir)

addProperties('fbneo')