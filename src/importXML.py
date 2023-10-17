#Skraper에서 만든 xml 리스트를 읽어서 포맷에 맞게 수정하는 스크립트

import os
from os import path
import xml.etree.ElementTree as ET

from config import Config

cfg = Config()

def readSkraperXmlFile(subRomDir):
    xmlPath = path.join(subRomDir, "game.xml")
    tree = ET.parse(xmlPath)
    games = tree.getroot()
    for game in games:
        # get name property of game
        name = game.attrib['name']
        print(name)
        


if __name__ == "__main__":
    currPath = os.getcwd()
    os.chdir(cfg.getBasePath())
    readSkraperXmlFile('fds')


