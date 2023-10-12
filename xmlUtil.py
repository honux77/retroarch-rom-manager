'''XML List Module'''
import os

import xml.etree.ElementTree as ET
from config import Config
from os import path

cfg = Config()

class XmlGameList:
    '''
    XML로 GameList 를 저장하고 관리한다.
    '''
    
    def __init__(self, subRomDir: str):
        '''
        Constructor: XML 파일을 읽어서 gameList를 생성한다.
        subRomDir: 서브 롬 디렉토리
        만약 XML 파일이 없으면 gameList를 생성하지 않는다.
        '''
        self.subRomDir = subRomDir
        self.xmlPath = path.join(subRomDir, cfg.getXmlName())
        self.tree = None
        self.gameList = None
        self.gameNodes = None

        if path.isfile(self.xmlPath):
            self.load(subRomDir)
        
    def load(self, subRomDir):
        '''
        XML 파일을 읽어서 gameList를 생성한다.
        subRomDir: 서브 롬 디렉토리
        '''
        self.subRomDir = subRomDir
        self._load()

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

    def __addNodeInGameNodes(self, game):
        '''
        gameNodes에 game을 추가한다.
        '''
        gameNode = ET.SubElement(self.gameNodes, 'game')
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
        서브 롬 디렉토리의 파일들을 읽고 gameList에 추가한다.
        파일들의 확장자는 config에서 설정한 확장자와 일치하는 파일만 추가한다.
        '''
        
        romFiles = [f for f in os.listdir(self.subRomDir) if path.isfile(path.join(self.subRomDir, f)) and path.splitext(f)[1][1:] in cfg.getExtension()]
        listFiles = [f['path'][2:] for f in self.gameList]
        append = False

        for romFile in romFiles:
            # listFiles에 없는 경우 XML 리스트에 추가한다.
            if romFile not in listFiles:
                game = {
                    'name': path.splitext(romFile)[0],
                    'path': './' + romFile,
                    'image': './media/images/' + path.splitext(romFile)[0] + '.png',
                    'rating': '0.6',
                    'desc': '{}의 설명입니다.'.format(path.splitext(romFile)[0]),
                }
                print("Add game: ", game)
                self.gameList.append(game)
                self.__addNodeInGameNodes(game)
                append = True        
        return append
        
    def _load(self):
        '''
        XML 파일을 읽어서 gameList를 생성한다.        
        '''        
        self.tree = ET.parse(self.xmlPath)
        self.gameNodes = self.tree.getroot()
        self.gameList = []
        update = False
        for gameNode in self.gameNodes:  
            # image path가 없는 경우 추가
            if gameNode.find('image') is None:
                self._createImagePath(gameNode)                
                update = True

            # image 경로가 ./ 로 시작하지 않으면 ./를 추가한다.
            if gameNode.find('image').text[:2] != './':
                gameNode.find('image').text = './' + gameNode.find('image').text
                gameNode.find('image').tail = '\n\t\t'
                update = True
            
            # rating이 없는 경우 추가
            if gameNode.find('rating') is None:
                rating = ET.SubElement(gameNode, 'rating')
                rating.text = '0.6'
                rating.tail = '\n\t\t'
                update = True

            # description이 없는 경우 추가
            if gameNode.find('desc') is None:
                desc = ET.SubElement(gameNode, 'desc')
                desc.text = '{}의 설명입니다.'.format(gameNode.find('name').text)
                desc.tail = '\n\t\t'
                update = True

            self.gameList.append(
                {
                    'name': gameNode.find('name').text,
                    'path': gameNode.find('path').text,
                    'image': gameNode.find('image').text,
                    'rating': gameNode.find('rating').text,
                    'desc': gameNode.find('desc').text,
                }
            )

        # 서브롬 디렉토리의 파일들을 읽고 gameList에 추가한다.
        append = self._addGameInSubRomDirectory()

        # sort by name
        self.gameList.sort(key=lambda x: x['name'])

        # update XML file
        if update or append:
            print("Update XML file: ", self.xmlPath)
            self.tree.write(self.xmlPath, 'UTF-8')
    
    def findGame(self, name):
        '''find game from gameList'''
        for game in self.gameList:
            if game['name'] == name:
                return game
        return None
    
    def _findGameNode(self, name):
        for game in self.gameNodes:
            if game.find('name').text == name:
                return game
        return None
    
    def getRomPath(self, romName):
        '''
        롬 이름을 받아서 롬 경로를 반환한다.
        해당 롬 이름의 경로가 없을 경우 None을 반환한다.
        '''
        return self.findGame(romName)['path']

    def getImagePath(self, romName):
        '''
        롬 이름을 받아서 이미지 경로를 반환한다.
        해당 롬 이름의 이미지가 없을 경우 None을 반환한다.
        '''
        return self.findGame(romName)['image']
    
    def updateGame(self, oldRomName, newGame, dryRun=False):
        '''
        롬 이름을 받아서 해당 롬 정보를 업데이트한다.
        '''      
        # xml 엘리먼트만 업데이트한다.
        # 마지막에 load를 호출하므로 전체 정보도 갱신이 된다.
        # 느려질 것 같긴 한데 일단 돌아가니 그냥 이렇게 두자.
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
            
    
# main function for test

if __name__ == '__main__':
    import os
    cfg = Config()
    os.chdir(cfg.getBasePath())
    
    # 로딩 테스트
    print("\n로딩 테스트")
    
    g = XmlGameList('gba-test')

    topGames = g.gameList[:10]
    

    print("Top 10 games: ")
    for game in topGames:
        print(game)
    

    # 롬 이름 검색 테스트
    name = g.gameList[0]['name']
    game = g.findGame(name)
    print(name, game, name == game['name'])

    ## 이미지 경로 테스트
    print("이미지 경로", g.getImagePath(name))

    ## 롬 삭제 테스트
    g.remove(name, dryRun=True)
    print("삭제 후 검색결과: ", g.findGame(name))
    print("삭제 후 Top 리스트: ", g.gameList[:5])
        