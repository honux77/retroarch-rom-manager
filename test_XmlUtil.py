#xml test

class TestXmlUtil:

    def setup_method(self):
        import config
        import xmlUtil
        import fileUtil        
        
        self.ROMDIR = 'anux'
        self.ROMSIZE = 8
        self.config = config.Config()
        fileUtil.changeSubRomDir(self.ROMDIR)
        self.xmlManager = xmlUtil.XmlManager()        

    def test_xml_create(self):
        # force delete GameList.xml        
        isCreate = self.xmlManager.createXML(force=True)
        assert isCreate == True
        assert self.xmlManager.size() == self.ROMSIZE

        isCreate = self.xmlManager.createXML()
        assert isCreate == False

        assert self.xmlManager.xmlRoot != None
        assert self.xmlManager.gameMap != None
        assert self.xmlManager.size() == self.ROMSIZE
    
    def test_loadXml(self):
        self.xmlManager.clear()
        assert self.xmlManager.xmlRoot == None          
        self.xmlManager.readGamesFromXml()
        assert self.xmlManager.xmlRoot != None
        assert self.xmlManager.gameMap != None
        assert self.xmlManager.size() == self.ROMSIZE

    def test_findGame(self):        
        self.xmlManager.reload()
        game = self.xmlManager.findGameByIdx(0)        
        assert game != None
        
        assert game == self.xmlManager.findGameByPath(game['path'])

        assert self.xmlManager.findGameByIdx(len(self.xmlManager.gameList)) == None

        game = self.xmlManager.findGameByPath("dsalkjfadsncxklvj3432afjkd")
        assert game == None
        
    def test_listSorted(self):
        self.xmlManager.reload()
        games = self.xmlManager.gameList
        assert len(games) == self.ROMSIZE
        for i in range(1, len(games)):
            print(games[i-1]['name'], games[i]['name'], "?")
            assert games[i]['name'] > games[i-1]['name']