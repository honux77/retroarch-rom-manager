from config import Config
from xmlUtil import XmlManager


from os import path
config = Config()
XmlManager = XmlManager()

def updateXMLFromScrapper(dryRun=True):
    '''
    스크래퍼에서 가져온 정보로 XML을 업데이트한다.
    return: 업데이트된 게임 수
    '''

    scrapGames =_importFromSkraperXmlFile()
    gameList = XmlManager.gameList
    skipWord = config.getScrapperSkipWord()    
    if scrapGames is None:
        return 0
    
    updateCount = 0
    skipCount = 0
    for game in gameList:
        oldpath = game['path']
        update = False

        if game['path'] in scrapGames:
            scrapGame = scrapGames[game['path']]
            
            # 한글 이름이 아니고 다른 내용이 있을 경우 업데이트한다.
                    # game['name'] 이 skipword로 시작하면 업데이트하지 않는다.
            if game['name'] != None and game['name'].startswith(skipWord):
                print(f"제목 변경 스킵: {game['name']}")
                skipCount += 1
                
            elif game['name'].isascii() and game['name'] != scrapGame['name']:
                print(f"Update game name: {game['path']} {game['name']} --> {scrapGame['name']}")
                game['name'] = scrapGame['name']
                update = True
            
            # 설명이 한글이 아니고 변경사항이 있을 경우만 업데이트한다.
            if scrapGame['desc'] != None and game['desc'].isascii() and game['desc'][:20] != scrapGame['desc'][:20]:
                print("Game desc before: ", game['path'], game['desc'])
                print("Game desc after: ", game['path'], scrapGames[game['path']]['desc'])
                game['desc'] = scrapGames[game['path']]['desc'].strip()
                update = True
            
            if update:
                updateCount += 1
                print("Update game: ", game['path'], end=' ')
                print(XmlManager.updateGame(oldpath, game, dryRun=True))
    
    if updateCount > 0:
        if not dryRun:
            print("Update {} games from skraper xml file".format(updateCount))
            XmlManager.save()            
    else:
        print("No game updated from skraper xml file")

    return updateCount


def _importFromSkraperXmlFile():        
    skraperXmlPath = config.getScrapperXmlName()
    scrapGames = {}

    if not path.isfile(skraperXmlPath):
        print("Skraper XML 파일이 없습니다. ", skraperXmlPath)        
        return None
    
    import xml.etree.ElementTree as ET
    skraperTree = ET.parse(skraperXmlPath)
    skraperRoot = skraperTree.getroot()
    gameNodes = skraperRoot.findall('game')
    
    for game in gameNodes:
        gname = game.attrib['name']
        gpath = "./" + game.find('rom').attrib['name']
        desc = game.find('description').text if game.find('description') is not None else f'Description of {gname}'            
        scrapGames[gpath] = {
            'name': gname,
            'path': gpath,
            'desc': desc
        }
    print("Skraper XML 파일 {}에서 {} 개의 게임정보를 읽었습니다. ".format(skraperXmlPath, len(scrapGames)))
    return len(scrapGames)