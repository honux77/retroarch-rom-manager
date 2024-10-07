class TestGroovy:

    def setup_method(self):
        import os    
        from os import path
        import config
        import fileUtil
        from xmlUtil import XmlManager

        SUBDIR = 'mame'

        fileUtil.changeSubRomDir(SUBDIR)
        self.config = config.Config()
        self.xmlManager = XmlManager()
        

    def test_readCsv(self):
        '''
        csv 파일을 읽는지 테스트
        '''
        import groovy
        groovyData = groovy.readCsv()
        for data in groovyData:
            print(data)
        assert len(groovyData) > 0

    def test_exportGroovyList(self):
        '''
        xml 파일을 읽어서 MAME 리스트로 변환하는지 테스트
        '''
        import groovy
        (match, total) = groovy.exportGroovyList(dryRun=False)
        assert match > 0 and total > 0
        assert match == total
