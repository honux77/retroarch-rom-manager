class SyncFile:
    '''
    원격지와 로컬의 롬 리스트와 파일을 동기화한다.
    '''

    def __init__(self):
        self.ssh = None
        self.connected = False
    
    def setServerInfo(self, serverInfo):        
        self.address = serverInfo['address']
        self.user = serverInfo['user']
        self.password = serverInfo['password']
        
    def connectSSH(self):
        import paramiko
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.address, username=self.user, password=self.password)        
        print("SSH 접속 성공: ", self.address)
        return True
    
    def disconnectSSH(self):        
        self.connected = False
        self.ssh.close()
        self.ssh = None
        print("SSH 접속 종료")

    def copyRemoteList(self):
        '''
        원격지의 게임 리스트를 로컬로 복사한다.
        현재는 groovy만 지원한다.
        '''
        import fileUtil
        from config import Config
        from os import path

        config = Config()
        groovy = config.getRemoteInfo('groovy')
        subRomDir = fileUtil.getCurrentRomDirName()
        listfilename = groovy['listFilename'][subRomDir]
        localPath = path.join(groovy['localListPath'], listfilename)
        # linux에서는 /로 경로를 구분해서 path.join을 사용하면 안된다.
        remotePath = groovy['remoteListPath'] +"/" + listfilename
            
        sftp = self.ssh.open_sftp()
        try:
            sftp.get(remotePath, localPath)
            print(f'{remotePath} -> {localPath} 복사 완료')
        except FileNotFoundError:
            print(f'{remotePath} 파일이 존재하지 않습니다.')
            return (None, None)
        finally:
            sftp.close()        
        return (localPath, remotePath)
        
        