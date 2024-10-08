from xmlUtil import XmlManager
from config import Config

def readCsv():
    '''
    그루비 리스트 폴더에서 ;으로 구분된 gamelist.txt 파일을 읽어서 리스트로 반환한다.    
    '''
    from os import path
    import fileUtil
    config = Config()
    
    with open(path.join(config.getGroovyListPath(),
                        config.getGroovyListFilename(fileUtil.getCurrentRomDirName())),
                        'r', encoding='utf-8') as f:
        import csv
        reader = csv.reader(f, delimiter=';')
        groovyData = []
        for row in reader:
            if row != []: # 빈 행은 제외
                groovyData.append(row)
    return groovyData[0], groovyData[1:] # header, data
    

def exportGroovyList(dryRun=False):
    '''
    현재 xml 파일을 읽어서 MAME 게임 리스트 형식으로 변환 저장한다.
    '''
    from config import Config
    import fileUtil
    config = Config()
    xmlManager = XmlManager()
    xmlManager.readGamesFromXml()
    header, groovyData = readCsv()

    gameMap = {}
    matchCount = 0

    from os import path
    for game in xmlManager.gameList:
        # key =  filname from path ./hello.zip -> hello
        filename = path.splitext(path.basename(game['path']))[0]
        print(filename)
        gameMap[filename] = game['name']

    
    for data in groovyData:
        if data[0] in gameMap:
            matchCount += 1
            print(f'파일명: {data[0]} 타이틀명: {gameMap[data[0]]}')
            data[1] = gameMap[data[0]]    
        else:
            print(f'파일명: {data[0]} **일치하는 타이틀 없음**')    
    
    if not dryRun:

        skipword = config.getGroovySkipWord()
        # write to file
        with open(path.join(config.getGroovyListPath(),
                        config.getGroovyListFilename(fileUtil.getCurrentRomDirName())),
                        'w', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f, delimiter=';')
            writer.writerow(header)
            for row in groovyData:                
                if row[1].startswith(skipword):
                    continue
                writer.writerow(row)

    print(f'{len(groovyData)} 게임 중 {matchCount}개 일치')
    return (matchCount,len(groovyData))
        
        

    
