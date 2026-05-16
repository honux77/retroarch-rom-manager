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
        self.remotePath = self.server['remoteListPath'] + "/" + listfilename
        print(f"서버 정보 설정 완료: {serverName} / {subRomDir}")
        
        
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
    

    def _sync_sftp_dir(self, sftp, local_dir, remote_dir, label, progress_fn, progress_offset, total):
        '''로컬 디렉토리와 원격 디렉토리를 양방향 동기화한다. (remove + upload)
        return: (removeCount, uploadCount)
        '''
        import os
        from os import path

        local_files = [f for f in os.listdir(local_dir) if path.isfile(path.join(local_dir, f))]

        # 원격 디렉토리 없으면 단계별 생성
        try:
            sftp.chdir(remote_dir)
        except IOError:
            print(f'원격 디렉토리 없음, 생성: {remote_dir}')
            cur = ''
            for part in remote_dir.strip('/').split('/'):
                cur += '/' + part
                try:
                    sftp.stat(cur)
                except IOError:
                    sftp.mkdir(cur)
            sftp.chdir(remote_dir)

        remote_files = sftp.listdir()

        # 원격에만 있는 파일 제거
        remove_count = 0
        for remote_file in remote_files:
            if remote_file not in local_files:
                try:
                    attr = sftp.stat(remote_file)
                    if attr.st_mode & 0o40000:
                        continue
                    sftp.remove(remote_file)
                    print(f'[{label}] 원격 제거: {remote_file}')
                    remove_count += 1
                except IOError as e:
                    print(f'[{label}] 원격 제거 실패 ({remote_file}): {e}')

        # 로컬에만 있는 파일 업로드
        upload_count = 0
        for i, local_file in enumerate(local_files):
            if local_file not in remote_files:
                try:
                    sftp.put(path.join(local_dir, local_file), local_file)
                    print(f'[{label}] 업로드: {local_file}')
                    upload_count += 1
                except IOError as e:
                    print(f'[{label}] 업로드 실패 ({local_file}): {e}')
            progress_fn(progress_offset + i + 1, total, f'{label} 동기화 중...')

        print(f'[{label}] 제거 {remove_count}개, 업로드 {upload_count}개')
        return remove_count, upload_count

    def syncSubRoms(self, subRomDir, status_window=None, status_label=None, progress_bar=None, callback=None):
        '''
        지정된 서브 롬 폴더의 롬 파일들을 SSH로 동기화한다.
        callback: optional function(current, total) for progress updates
        return: (removeRomCount, removeImageCount, uploadRomCount, uploadImageCount, totalLocalRomCount, totalLocalImageCount)
        '''

        from config import Config
        config = Config()

        def update_progress(current, total, message=""):
            if callback:
                callback(current, total)
            elif status_window and status_label and progress_bar:
                progress = int((current / total) * 100) if total > 0 else 0
                status_label.config(text=message or f'동기화 중... {progress}% 완료')
                progress_bar['value'] = progress
                status_window.update_idletasks()

        import fileUtil
        fileUtil.cleanRomFolder()

        if not self.connected:
            print("SSH에 연결되어 있지 않습니다.")
            return -1, -1

        import os
        from os import path

        localBasePath = path.join(config.getBasePath(), subRomDir)
        localImagePath = path.join(localBasePath, 'media', 'images')

        # 파일만 포함 (디렉토리 제외) — media 폴더 등을 sftp.put 하면 실패함
        localFileList = [f for f in os.listdir(localBasePath)
                         if path.isfile(path.join(localBasePath, f))]
        localImageList = [f for f in os.listdir(localImagePath)
                          if path.isfile(path.join(localImagePath, f))]

        total_files = len(localFileList) + len(localImageList)

        sftp = self.ssh.open_sftp()
        try:
            remoteRomDir = self.server['remoteRomPath'] + '/' + subRomDir
            try:
                sftp.chdir(remoteRomDir)
            except IOError:
                print(f'원격 롬 디렉토리 없음, 생성: {remoteRomDir}')
                sftp.mkdir(remoteRomDir)
                sftp.chdir(remoteRomDir)

            remoteFileList = sftp.listdir()

            # 원격에만 있는 파일 제거
            removeRomCount = 0
            for remoteFile in remoteFileList:
                if remoteFile not in localFileList:
                    try:
                        fileAttr = sftp.stat(remoteFile)
                    except IOError as e:
                        print(f'원격 파일 정보 조회 실패 ({remoteFile}): {e}')
                        continue
                    if fileAttr.st_mode & 0o40000:  # 디렉토리면 스킵
                        continue
                    try:
                        sftp.remove(remoteFile)
                        print(f'원격에서 제거: {remoteFile}')
                        removeRomCount += 1
                    except IOError as e:
                        print(f'원격 파일 제거 실패 ({remoteFile}): {e}')

            print(f'원격에서 제거된 롬 파일 수: {removeRomCount}')

            # 로컬에만 있는 파일 업로드
            uploadRomCount = 0
            for i, localFile in enumerate(localFileList):
                if localFile not in remoteFileList:
                    localFilePath = path.join(localBasePath, localFile)
                    try:
                        sftp.put(localFilePath, localFile)
                        print(f'원격에 업로드: {localFile}')
                        uploadRomCount += 1
                    except IOError as e:
                        print(f'롬 업로드 실패 ({localFile}): {e}')
                update_progress(i + 1, total_files, f'{subRomDir} 롬 동기화 중...')

            print(f'원격에 업로드된 롬 파일 수: {uploadRomCount}')

            # 이미지 디렉토리 동기화
            remoteImageDir = self.server['remoteImagePath'].replace('[SUB]', subRomDir)
            removeImageCount, uploadImageCount = self._sync_sftp_dir(
                sftp, localImagePath, remoteImageDir,
                f'{subRomDir}/images', update_progress,
                progress_offset=len(localFileList),
                total=total_files,
            )

        finally:
            sftp.close()

        return (removeRomCount, removeImageCount, uploadRomCount, uploadImageCount,
                len(localFileList), len(localImageList))
           
       

        
        