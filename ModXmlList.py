'''XML List Module'''

import xml.etree.ElementTree as ET

listFile = "gamelist.xml"


def getXmlList(subRomDir):
    '''Get XML List'''
    # open xml file

    tree = ET.parse(listFile)
    games = tree.getroot()


    