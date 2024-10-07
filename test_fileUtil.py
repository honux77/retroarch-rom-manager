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

    def test_getCurrentRomDirName(self):
        '''
        하위 디렉토리를 읽는지 테스트
        '''
        import fileUtil
        subdir = fileUtil.getCurrentRomDirName()
        assert subdir == self.SUBDIR

    def test_getRomCount(self):
        '''
        하위 디렉토리의 파일 갯수를 읽는지 테스트
        '''
        import fileUtil
        count = fileUtil.getRomCount()
        print(f"서브롬 디렉토리 {self.SUBDIR}의 롬파일 갯수: {count}")
        assert count > 3
        

    