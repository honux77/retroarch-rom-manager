class SyncFile:
    '''
    원격지와 로컬의 롬 리스트와 파일을 동기화한다.
    '''

    def __init__(self):
        self.ssh = None
        self.connected = False
    
    def setServerInfo(self, serverName):        
        from os import path
        from config import Config
        import fileUtil
        
        config = Config()
        subRomDir = fileUtil.getCurrentRomDirName()
        server = config.getServerInfo(serverName)
        serverInfo = server['serverInfo']
        self.address = serverInfo['address']
        self.user = serverInfo['user']
        self.password = serverInfo['password']        
        
        listfilename = server['listFilename'][subRomDir]
        self.localPath = path.join(server['localListPath'], listfilename)
        # linux에서는 /로 경로를 구분해서 path.join을 사용하면 안된다.
        self.remotePath = server['remoteListPath'] +"/" + listfilename
        
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
        sftp = self.ssh.open_sftp()
        try:
            sftp.get(self.remotePath, self.localPath)
            print(f'{self.remotePath} -> {self.localPath} 복사 완료')
        except FileNotFoundError:
            print(f'{self.remotePath} 파일이 존재하지 않습니다.')
            return (None, None)
        finally:
            sftp.close()        
        return (self.localPath, self.remotePath)
    
    def exportLocalList(self):
        '''
        로컬 롬 리스트를 서버로 업로드한다.
        '''
        sftp = self.ssh.open_sftp()
        try:
            sftp.put(self.localPath, self.remotePath)
            print(f'{self.localPath} -> {self.remotePath} 복사 완료')
        except FileNotFoundError:
            print(f'{self.localPath} 파일이 존재하지 않습니다.')
            return (None, None)
        finally:
            sftp.close()
        return (self.localPath, self.remotePath)
        
        