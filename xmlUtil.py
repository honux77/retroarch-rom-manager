'''XML List Module'''
import os

import xml.etree.ElementTree as ET
from os import path

from config import Config
from decorator import singleton

cfg = Config()

@singleton
class XmlManager:
    '''
    XML을 읽고 처리하는 클래스 
    xml 안의 game을 map으로 관리한다.
    '''
    
    def __init__(self):
        '''
        Constructor: 현재 디렉토리에서 XML 파일을 읽어서 gameMap을 생성한다.        
        만약 XML 파일이 없으면 새로 XML 파일을 생성한다.
        '''
        self.xmlPath = cfg.getXmlName() 
        self.clear()

        if not path.isfile(self.xmlPath):
            self.createXML()
        self.updateList()

    def updateList(self):
        '''
        gameList를 gameMap에서 생성한다.
        '''
        self.gameList = sorted(list(self.gameMap.values()), key=lambda x: x['name'])
    
    def reload(self):
        if self.gameMap is None or len(self.gameMap) == 0:
            self.readGamesFromXml()
        if self.gameList is None or len(self.gameList) == 0:
            self.updateList()

    
    def clear(self):
        '''
        tree, xmlRoot, gameMap, gameList를 초기화한다.
        '''
        self.tree = None
        self.xmlRoot = None
        self.gameMap = {}
        self.gameList = []

    def createXML(self, force=False):
        '''
        게임리스트 XML 파일이 존재하지 않으면 새로 생성한다.
        force: True인 경우 기존 XML 파일을 삭제하고 새로 생성한다.        
        '''
        print(path.isfile(self.xmlPath))
        if force and path.isfile(self.xmlPath):
            print("기존 XML 파일을 삭제합니다. ", self.xmlPath)
            self.clear()
            os.remove(self.xmlPath)            
        
        if not path.isfile(self.xmlPath):
            print("XML 파일이 없습니다. ", self.xmlPath)
            print("새로운 XML 파일을 생성합니다.")
            self.clear()
            self.tree = ET.ElementTree(ET.Element('gameList'))
            self.xmlRoot = self.tree.getroot()            
            self._addGameInSubRomDirectory()
            self.tree.write(self.xmlPath, 'UTF-8')            
            return True
        print("XML 파일이 이미 존재합니다. ", self.xmlPath)
        return False
        
    def readGamesFromXml(self):
        '''
        XML 파일을 읽어서 gameMap을 생성한다.
        subRomDir: 서브 롬 디렉토리
        '''
        self.clear()
        self._load()        
        self._updateFromScrapper()

    def save(self):
        '''
        gameList를 XML 파일에 저장한다.
        '''
        self.tree.write(self.xmlPath, 'UTF-8')

    def _createImagePath(gameNode):
        '''
        image path가 없는 경우 추가
        '''        
        image = ET.SubElement(gameNode, 'image')
        # get filename without extension
        fileName = path.splitext(gameNode.find('path').text)[0][2:]
        image.text =  "./media/images/" + fileName + ".png"
        image.tail = '\n\t\t'  

    def _addNodeInGameNodes(self, game):
        '''
        xmlRoot에 game을 추가한다.
        '''
        gameNode = ET.SubElement(self.xmlRoot, 'game')
        name = ET.SubElement(gameNode, 'name')
        name.text = game['name']
        name.tail = '\n\t\t'
        path = ET.SubElement(gameNode, 'path')
        path.text = game['path']
        path.tail = '\n\t\t'
        image = ET.SubElement(gameNode, 'image')
        image.text = game['image']
        image.tail = '\n\t\t'
        rating = ET.SubElement(gameNode, 'rating')
        rating.text = game['rating']
        rating.tail = '\n\t\t'
        desc = ET.SubElement(gameNode, 'desc')
        desc.text = game['desc']
        desc.tail = '\n\t\t'


    def _addGameInSubRomDirectory(self):
        '''
        리스트에 누락된 파일들을 추가
        서브 롬 디렉토리의 파일들을 읽어 gameMap과 xmlRoot에 추가한다.
        파일들의 확장자는 config에서 설정한 확장자와 일치하는 파일만 추가한다.
        '''

        from fileUtil import getExtension
        from fileUtil import getFileNameWithoutExt
        
        romFiles = [f for f in os.listdir() if path.isfile(f) and getExtension(f) in cfg.getExtension()]
        
        append = False
        for romFile in romFiles:
            # listFiles에 없는 경우 XML 리스트에 추가한다.
            if romFile not in self.gameMap:
                game = {
                    'name': getFileNameWithoutExt(romFile),
                    'path': './' + romFile,
                    'image': './media/images/' + getFileNameWithoutExt(romFile) + '.png',
                    'rating': '0.6',
                    'desc': '{} is a good game!'.format(getFileNameWithoutExt(romFile)),
                }
                print("Add game: ", game)
                self.gameMap[romFile] = game
                self._addNodeInGameNodes(game)
                append = True                
        return append
    
    def _importFromSkraperXmlFile(self):        
        skraperXmlPath = cfg.getScrapperXmlName()
        if not path.isfile(skraperXmlPath):
            print("Skraper XML 파일이 없습니다. ", skraperXmlPath)
            self.scrapGames = None
            return 0
        
        skraperTree = ET.parse(skraperXmlPath)
        skraperRoot = skraperTree.getroot()
        gameNodes = skraperRoot.findall('game')
        self.scrapGames = {}
        for game in gameNodes:
            gname = game.attrib['name']
            gpath = "./" + game.find('rom').attrib['name']
            desc = game.find('description').text if game.find('description') is not None else f'Description of {gname}'            
            self.scrapGames[gpath] = {
                'name': gname,
                'path': gpath,
                'desc': desc
            }
        print("Skraper XML 파일 {}에서 {} 개의 게임정보를 읽었습니다. ".format(skraperXmlPath, len(self.scrapGames)))
        #os.remove(skraperXmlPath)
        return len(self.scrapGames)
    
    def _updateFromScrapper(self):
        self._importFromSkraperXmlFile()
        if self.scrapGames is None:
            return
        updateCount = 0
        for game in self.gameMap.values:
            oldName = game['name']
            update = False
            if game['path'] in self.scrapGames:
                
                # 한글 이름이 아니고 다른 내용이 있을 경우 업데이트한다.
                if game['name'].isascii() and game['name'] != self.scrapGames[game['path']]['name']:
                    print("Update game name: ", game['path'], game['name'], self.scrapGames[game['path']]['name'])
                    game['name'] = self.scrapGames[game['path']]['name']
                    update = True
                
                # 설명이 한글이 아니고 변경사항이 있을 경우만 업데이트한다.
                if game['desc'].isascii() and game['desc'][:20] != self.scrapGames[game['path']]['desc'][:20]:
                    print("Update game desc before: ", game['path'], game['desc'])
                    print("Update game desc after: ", game['path'], self.scrapGames[game['path']]['desc'])
                    game['desc'] = self.scrapGames[game['path']]['desc'].strip()
                    update = True
                
                if update:
                    updateCount += 1
                    print("Update game: ", game['path'], end=' ')
                    print(self.updateGame(oldName, game, dryRun=True))
        
        if updateCount > 0:
            print("Update {} games from skraper xml file".format(updateCount))
            self.save()
        else:
            print("No game updated from skraper xml file")
        
    def _removeAllSubElements(self, element, pName):
        '''
        element의 모든 서브 엘리먼트를 제거한다.
        <desc /> 속성으로 버그가 발생해서 해결하기 위해 작성
        TODO: 더 좋은 방법은 없는지 찾아보자.
        '''
        for subElement in element.findall(pName):
            element.remove(subElement)
    
    def _load(self):
        '''
        XML 파일을 읽어서 tree, xmlRoot, gameMap, gameList를 생성한다.        
        '''        
        self.clear()
        self.tree = ET.parse(self.xmlPath)
        self.xmlRoot = self.tree.getroot()        
        update = False
        for gameNode in self.xmlRoot.findall('game'):            

            # path가 ./로 시작하지 않는 경우 ./ 추가
            if gameNode.find('path').text[:2] != './':
                gameNode.find('path').text = './' + gameNode.find('path').text
                gameNode.find('path').tail = '\n\t\t'

                print("Path 경로 수정: {} {}".format(gameNode.find('name').text, gameNode.find('path').text))
                update = True

            # image path가 없는 경우 추가
            if gameNode.find('image') is None:
                self._createImagePath(gameNode)      

                print("Image 경로 추가: {} {}".format(gameNode.find('name').text, gameNode.find('image').text))          
                update = True

            # image 경로가 ./ 로 시작하지 않으면 ./를 추가한다.
            if gameNode.find('image').text[:2] != './':
                gameNode.find('image').text = './' + gameNode.find('image').text
                gameNode.find('image').tail = '\n\t\t'

                print("Image 경로 수정: {} {}".format(gameNode.find('name').text, gameNode.find('image').text))
                update = True
            
            # rating이 없는 경우 추가
            if gameNode.find('rating') is None:
                rating = ET.SubElement(gameNode, 'rating')
                rating.text = '0.6'
                rating.tail = '\n\t\t'

                print("Rating 추가: {} {}".format(gameNode.find('name').text, gameNode.find('rating').text))
                update = True

            # description이 없는 경우 추가
            if gameNode.find('desc') is None or gameNode.find('desc').text is None:                
                self._removeAllSubElements(gameNode, 'desc')
                desc = ET.SubElement(gameNode, 'desc')
                desc.text = '{} is a good game!'.format(gameNode.find('name').text)
                desc.tail = '\n\t\t'

                print("Description 추가: {} {}".format(gameNode.find('name').text, gameNode.find('desc').text))
                update = True

            romName = path.basename(gameNode.find('path').text)
            self.gameMap[romName] = {             
                    'name': gameNode.find('name').text,
                    'path': gameNode.find('path').text,
                    'image': gameNode.find('image').text,
                    'rating': gameNode.find('rating').text,
                    'desc': gameNode.find('desc').text,
                }            

        # 서브롬 디렉토리의 파일들을 읽고 gameList에 추가한다.
        append = self._addGameInSubRomDirectory()

        # update XML file
        if update or append:
            print("Update XML file: ", self.xmlPath)
            self.tree.write(self.xmlPath, 'UTF-8')
        
        self.updateList()
        print(f"게임 리스트 XML 파일 {self.xmlPath}에서 {len(self.gameMap)} 개의 게임정보를 읽었습니다. ")

    def findGame(self, romfile):
        '''
        롬 경로를 받아서 해당 롬 정보를 반환한다.
        해당 롬 경로가 없을 경우 None을 반환한다.
        '''
        if romfile in self.gameMap:
            return self.gameMap[romfile]
        return None
    
    def findByIdx(self, idx):
        '''
        인덱스로 게임을 찾는다.
        '''
        if idx < len(self.gameList):
            return self.gameList[idx]
        return None
        
    
    def _findGameNode(self, name):
        for game in self.xmlRoot.findall('game'):
            if game.find('name').text == name:
                return game
        return None
    
    def getRomPath(self, romPath):
        '''
        롬 이름을 받아서 롬 경로를 반환한다.
        해당 롬 이름의 경로가 없을 경우 None을 반환한다.
        '''
        return self.findGame(path.basename(romPath))['path']

    def getImagePath(self, romPath):
        '''
        롬 이름을 받아서 이미지 경로를 반환한다.
        해당 롬 이름의 이미지가 없을 경우 None을 반환한다.
        '''        
        return self.findGame(romPath)['image']
    
    def updateGame(self, oldRomName, newGame:dict, dryRun=False):
        '''
        롬 이름을 받아서 해당 롬 정보를 업데이트한다.
        dryRun이 True인 경우 XML 파일을 업데이트하지 않는다.
        newGame: 업데이트할 롬 정보 딕셔너리
        '''
        # xml 엘리먼트만 업데이트한다.                
        gameNode = self._findGameNode(oldRomName)
        if gameNode is None:
            return False
        gameNode.find('name').text = newGame['name']
        gameNode.find('path').text = newGame['path']
        gameNode.find('image').text = newGame['image']
        gameNode.find('rating').text = newGame['rating']
        gameNode.find('desc').text = newGame['desc']
        
        if not dryRun:
            self.tree.write(self.xmlPath, 'UTF-8')
            self.load(self.subRomDir)
        return True
    
    def remove(self, romName, dryRun=False):
        '''
        롬 이름을 받아서 해당 롬을 리스트에서 제거한다.
        '''

        # gameList에서 제거
        game = self.findGame(romName)
        if game is None:
            return False
        self.gameList.remove(game)        

        # XML 엘리먼트도 제거
        game = self._findGameNode(romName)
        if game is None:
            return False
        self.gameNodes.remove(game)

        if not dryRun:
            self.tree.write(self.xmlPath, 'UTF-8')
            self.load(self.subRomDir)
        return True        
   