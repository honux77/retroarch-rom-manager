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
        print(f"설정 파일에서 {subRomDir} 롬 폴더에 대한 리스트 파일 정보를 찾을 수 없습니다.")            
        
        
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
    
    # match, total = syncFile.syncSubRoms()    
    def syncSubRoms(self):
        import tkinter as tk
        from tkinter import ttk
        import os
        import threading

        # 진행 상태 창 생성
        progress_window = tk.Toplevel()
        progress_window.title("롬 동기화")
        progress_window.geometry("300x150")

        # 진행 상태 라벨
        status_label = ttk.Label(progress_window, text="동기화 중...")
        status_label.pack(pady=10)

        # 진행바 
        progress_bar = ttk.Progressbar(progress_window, length=200, mode='determinate')
        progress_bar.pack(pady=10)

        def sync_thread():
            import fileUtil
            from config import Config
            config = Config()

            sftp = self.ssh.open_sftp()
            try:
                # 로컬 폴더의 모든 롬 파일 목록
                local_files = []
                for root, dirs, files in os.walk(fileUtil.getCurrentRomDirName()):
                    for file in files:
                        if file
                        local_files.append(os.path.join(root, file))

                total = len(local_files)
                uploaded = 0

                # 각 파일 업로드
                for local_file in local_files:
                    config.getExtensions()
                    if not progress_window.winfo_exists():
                        break
                        
                    remote_path = self.remotePath + "/" + os.path.basename(local_file)
                    status_label.config(text=f"업로드 중: {os.path.basename(local_file)}")
                    
                    try:
                        sftp.put(local_file, remote_path)
                        uploaded += 1
                        progress = (uploaded / total) * 100
                        progress_bar['value'] = progress
                        progress_window.update()
                    except:
                        print(f"업로드 실패: {local_file}")

                if progress_window.winfo_exists():
                    progress_window.destroy()
                return uploaded, total

            finally:
                sftp.close()

        # 동기화 스레드 시작
        sync_thread = threading.Thread(target=sync_thread)
        sync_thread.start()

        # 창이 닫힐 때까지 대기
        progress_window.wait_window()
        
        return 0, 0  # 취소된 경우 0,0 반환

        
        