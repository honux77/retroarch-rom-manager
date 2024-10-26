class TestScrapper:

    def test_scrapper(self):
    
        import os    
        from os import path
        import config
        import fileUtil

        config = config.Config()
        SUBDIR = 'anux'        
        fileUtil.changeSubRomDir(SUBDIR)

        from xmlUtil import XmlManager
        from scrapper import updateXMLFromScrapper

        xmlManager = XmlManager()
    
        assert xmlManager.size() > 0
        
        skip, update = updateXMLFromScrapper()    
        assert skip > 0
        assert update >= 0