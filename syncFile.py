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
        self.server = config.getServerInfo(serverName)
        serverInfo = self.server['serverInfo']
        self.address = serverInfo['address']
        self.user = serverInfo['user']
        self.password = serverInfo['password']        
        
        listfilename = self.server['listFilename'][subRomDir]
        self.localPath = path.join(self.server['localListPath'], listfilename)
        # linux에서는 /로 경로를 구분해서 path.join을 사용하면 안된다.
        self.remotePath = self.server['remoteListPath'] +"/" + listfilename
        print(f"설정 파일에서 {subRomDir} 롬 폴더에 대한 리스트 파일 정보를 찾을 수 없습니다.")            
        
        
    def connectSSH(self):
        import paramiko
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.address, username=self.user, password=self.password)        
        print("SSH 접속 성공: ", self.address)
        self.connected = True
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
    

    def syncSubRoms(self, subRomDir, status_window, status_label, progress_bar):
        '''
        지정된 서브 롬 폴더의 롬 파일들을 SSH로 동기화한다.
        return: (removeRomCount, removeImageCount, uploadRomCount, uploadImageCount, totalLocalRomCount, totalLocalImageCount)
        '''

        from config import Config
        config = Config()


        #시작전 manual 폴더 삭제
        import fileUtil
        fileUtil.cleanRomFolder()

        if not self.connected:
            print("SSH에 연결되어 있지 않습니다.")
            return -1,-1

        # 서브롬 폴더와 서버의 ~/shared/<subRomDir> 폴더를 비교하고 동기화한다.
        # 1. 로컬 폴더 목록 읽기, 하위 폴더와 파일도 모두 포함한다.
        import os
        from os import path
        localBasePath = path.join(config.getBasePath(), subRomDir)
        localImagePath = path.join(localBasePath, 'media', 'images')
        localFileList = os.listdir(localBasePath)
        localImageList = os.listdir(localImagePath)

        sftp = self.ssh.open_sftp()
        sftp.chdir(self.server['remoteRomPath'] + '/' + subRomDir)
        remoteFileList = sftp.listdir()

        # 원격에만 있는 파일 조회 후 제거
        removeRomCount = 0
        for remoteFile in remoteFileList:
            if remoteFile not in localFileList:
                #원격에만 있는 파일이 디렉토리라면 스킵
                try:
                    fileAttr = sftp.stat(remoteFile)
                    if fileAttr.st_mode & 0o40000: #디렉토리인 경우
                        continue
                except IOError:
                    continue

                print(f'원격에서 제거: {remoteFile}')
                sftp.remove(remoteFile)
                removeRomCount += 1
        
        print(f'원격에서 제거된 파일 수: {removeRomCount}')
        
        # 로컬에만 있는 파일 조회 후 업로드
        uploadRomCount = 0       
        totalRomCount = 0 
        for localFile in localFileList:
            totalRomCount += 1
            if localFile not in remoteFileList:
                #로컬에만 있는 파일
                localFilePath = path.join(localBasePath, localFile)
                sftp.put(localFilePath, localFile)
                print(f'원격에 업로드: {localFile}')
                uploadRomCount += 1
            #진행 상태 업데이트
            progress = int((totalRomCount / (len(localFileList) + len(localImageList))) * 100)
            status_label.config(text=f'{subRomDir} 롬 동기화 중... {progress}% 완료')
            progress_bar['value'] = progress
            status_window.update_idletasks()

        print(f'원격에 업로드된 파일 수: {uploadRomCount}')

        # 원격에만 있는 이미지 파일 조회 후 제거
        removeImageCount = 0
        sftp.chdir(self.server['remoteImagePath'].replace('[SUB]', subRomDir))  
        remoteImageList = sftp.listdir()
        for remoteImage in remoteImageList:
            if remoteImage not in localImageList:
                print(f'원격에서 제거: {remoteImage}')
                sftp.remove(remoteImage)
                removeImageCount += 1
        
        print(f'원격에서 제거된 이미지 파일 수: {removeImageCount}')

        # 원격에만 있는 이미지 파일 조회 후 업로드
        uploadImageCount = 0
        totalImageCount = 0
        for localImage in localImageList:
            totalImageCount += 1
            if localImage not in remoteImageList:
                #로컬에만 있는 이미지 파일
                localImageFilePath = path.join(localImagePath, localImage)
                sftp.put(localImageFilePath, localImage)
                print(f'원격에 업로드: {localImage}')
                uploadImageCount += 1
            
            #진행 상태 업데이트
            progress = int(((totalRomCount + totalImageCount) / (len(localFileList) + len(localImageList))) * 100)
            status_label.config(text=f'{subRomDir} 이미지 동기화 중... {progress}% 완료')
            progress_bar['value'] = progress

        return (removeRomCount, removeImageCount, uploadRomCount, uploadImageCount, len(localFileList), len(localImageList))
           
       

        
        