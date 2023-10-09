'''XML List Module'''

import xml.etree.ElementTree as ET
import config
from os import path

class GameList:
    '''GameList Class'''
    def __init__(self, romDir):
        self.romDir = romDir
        self.xmlPath = path.join(romDir, config.XML_LIST)
        self.load(romDir)
        

    def load(self, romDir):
        '''load XML List File'''        
        from os import path
        self.tree = ET.parse(self.xmlPath)
        self.games = self.tree.getroot()
        self.gameList = []
        for game in self.games:            
            self.gameList.append(
                {
                    'name': game.find('name').text,
                    'path': game.find('path').text,
                    'image': game.find('image').text,
                    'rating': game.find('rating').text
                }
            )
    
    def findGame(self, name):
        '''find game from gameList'''
        for game in self.gameList:
            if game['name'] == name:
                return game
        return None
    
# main function for test

if __name__ == '__main__':
    import os
    os.chdir(config.ROM_PATH)
    g = GameList('gb')
    name = g.gameList[0]['name']
    game = g.findGame(name)
    print(name, game, name == game['name'])


        