#xml test

class TestXmlUtil:

    def setup_method(self):
        import xmlUtil
        import config
        import os
        self.ROMDIR = 'anux'
        self.config = config.Config()
        os.chdir(self.config.getBasePath())
        self.xmlManager = xmlUtil.XmlManager(self.ROMDIR)        

    def test_xml_create(self):
        # delete GameList.xml        
        isCreate = self.xmlManager.createXML(force=True)
        assert isCreate == True
        isCreate = self.xmlManager.createXML()
        assert isCreate == False
    
    def test_loadXml(self):
        self.xmlManager.loadXml()
        assert len(self.xmlManager.getXml()) > 0