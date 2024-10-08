

def test_scrapper():
    
    import os    
    from os import path
    import config
    import fileUtil
    from xmlUtil import XmlManager
    from scrapper import updateXMLFromScrapper

    SUBDIR = 'mame'
    fileUtil.changeSubRomDir(SUBDIR)
    config = config.Config()
    xmlManager = XmlManager()
    
    skip, update = updateXMLFromScrapper()
    assert skip > 0
    assert update > 0