class TestFileUtil:

    def setup_method(self):
        import fileUtil
        import config
        self.config = config.Config()
        self.SUBDIR = 'anux'

    def test_chroot(self):
        '''
        설정한 기본디렉토리로 이동이 되는지 테스트
        '''
        import os    
        import fileUtil
        fileUtil.changeRootDir()
        assert os.getcwd() == self.config.getBasePath()

    def test_chsubdir(self):
        '''
        설정한 기본디렉토리로 이동이 되는지 테스트
        '''
        import os    
        import fileUtil
        fileUtil.changeSubRomDir(self.SUBDIR)
        assert os.getcwd() == self.config.getBasePath() + '\\' + self.SUBDIR

    