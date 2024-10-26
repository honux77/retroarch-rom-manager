import syncFile

class TestSyncFile:

    def setup_method(self):
        from config import Config        
        from syncFile import SyncFile
        import fileUtil        
        config = Config()
        self.syncFile = SyncFile()

        host = "groovy"
        subrom = "gb"
        fileUtil.changeSubRomDir(subrom)
        
        self.syncFile.setServerInfo(host)
        connected = self.syncFile.connectSSH()
        assert connected == True

    def alive(self):
        assert self.syncFile.connected == True

    def teardown_method(self):
        self.syncFile.disconnectSSH()

    def test_copyRemoteList(self):
        result = self.syncFile.copyRemoteList()
        print(result)        
        assert result[0] != None
        assert result[1] != None

    def test_exportLocalList(self):
        result = self.syncFile.exportLocalList()
        print(result)        
        assert result[0] != None
        assert result[1] != None
        
   