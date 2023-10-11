'''XML List Module'''

import xml.etree.ElementTree as ET
import config
from os import path

class XmlGameList:
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
        update = False
        for game in self.games:  

            # image path가 없는 경우 추가
            if game.find('image') is None:
                image = ET.SubElement(game, 'image')
                # get filename without extension
                fileName = path.splitext(game.find('path').text)[0][2:]
                image.text =  "./media/images/" + fileName + ".png"
                image.tail = '\n\t\t'
                update = True

            # image 경로가 ./ 로 시작하지 않으면 ./를 추가한다.
            if game.find('image').text[:2] != './':
                game.find('image').text = './' + game.find('image').text
                game.find('image').tail = '\n\t\t'
                update = True
            
            # rating이 없는 경우 추가
            if game.find('rating') is None:
                rating = ET.SubElement(game, 'rating')
                rating.text = '0.6'
                rating.tail = '\n\t\t'
                update = True

            # description이 없는 경우 추가
            if game.find('desc') is None:
                desc = ET.SubElement(game, 'desc')
                desc.text = '{}의 설명입니다.'.format(game.find('name').text)
                desc.tail = '\n\t\t'
                update = True

            self.gameList.append(
                {
                    'name': game.find('name').text,
                    'path': game.find('path').text,
                    'image': game.find('image').text,
                    'rating': game.find('rating').text,
                    'desc': game.find('desc').text,
                }
            )

        # sort by name
        self.gameList.sort(key=lambda x: x['name'])

        # update XML file
        if update:
            print("Update XML file: ", self.xmlPath)
            self.tree.write(self.xmlPath, 'UTF-8')
    
    def findGame(self, name):
        '''find game from gameList'''
        for game in self.gameList:
            if game['name'] == name:
                return game
        return None
    
    def _findGameNode(self, name):
        for game in self.games:
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
            self.load(self.romDir)
    
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
        self.games.remove(game)

        if not dryRun:
            self.tree.write(self.xmlPath, 'UTF-8')
            self.load(self.romDir)
        return True
            
    
# main function for test

if __name__ == '__main__':
    import os
    os.chdir(config.ROM_PATH)
    
    # 로딩 테스트
    g = XmlGameList('gb')

    topGames = g.gameList[:5]
    print("Top 5 games: ", topGames)

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
        