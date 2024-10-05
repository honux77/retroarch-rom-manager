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