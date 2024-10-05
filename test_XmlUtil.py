#xml test

class TestXmlUtil:

    def setup_method(self):
        import config
        import xmlUtil
        import fileUtil        
        
        self.ROMDIR = 'anux'
        self.config = config.Config()
        fileUtil.changeSubRomDir(self.ROMDIR)
        self.xmlManager = xmlUtil.XmlManager()        

    def test_xml_create(self):
        # force delete GameList.xml        
        isCreate = self.xmlManager.createXML(force=True)
        assert isCreate == True

        isCreate = self.xmlManager.createXML()
        assert isCreate == False

        assert self.xmlManager.xmlRoot != None
        assert self.xmlManager.gameMap != None
        assert len(self.xmlManager.gameMap.values()) > 0
    
    def test_loadXml(self):
        self.xmlManager.clear()
        assert self.xmlManager.xmlRoot == None          
        self.xmlManager.readGamesFromXml()
        assert self.xmlManager.xmlRoot != None
        assert self.xmlManager.gameMap != None
        assert len(self.xmlManager.gameMap.values()) > 0

    def test_findGame(self):        
        self.xmlManager.reload()
        game = self.xmlManager.findByIdx(0)        
        assert game != None

        from os import path
        filename = path.basename(game['path'])
        assert game == self.xmlManager.findGame(filename)

        game = self.xmlManager.findGame('1942a')
        assert game == None
        
    def test_listSorted(self):
        self.xmlManager.reload()
        games = self.xmlManager.gameList
        assert len(games) > 0
        for i in range(1, len(games)):
            assert games[i]['name'] > games[i-1]['name']