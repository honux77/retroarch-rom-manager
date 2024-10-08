#xml test

class TestXmlUtil:

    def setup_method(self):
        import config
        import xmlUtil
        import fileUtil        
        
        self.ROMDIR = 'anux'

        self.config = config.Config()        
        fileUtil.changeSubRomDir(self.ROMDIR)
        self.ROMSIZE = fileUtil.getRomCount()        
        self.xmlManager = xmlUtil.XmlManager()        

    def test_init(self):
        print(self.xmlManager.gameList)
        assert self.xmlManager.size() == self.ROMSIZE

    def test_xml_create(self):
        # force delete GameList.xml        
        count = self.xmlManager.createXML(force=True)
        assert count == self.ROMSIZE

        count = self.xmlManager.createXML()
        assert count == 0

        assert self.xmlManager.xmlRoot == None        
        assert self.xmlManager.gameMap == {}
        assert self.xmlManager.size() == 0
    
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