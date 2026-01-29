# simple GUI Frontend for RetroArch
import os
from os import path

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import Text
from tkinter import simpledialog
from tkinter import messagebox as mBox

from PIL import ImageTk, Image

# deepL translator
import translate

# local module
import xmlUtil
import fileUtil
import config
import lastStatus
import mainHandler
import retroTheme


# load config
config = config.Config()

mainHandler.initMainProgram(config)

# load lastStatus
status = lastStatus.LastStatus()

# global variable
lastRomIdx = status.getLastRomIdx()
lastSubRomDir = status.getLastSubRomDirectory()
programPath = os.getcwd()

# Create instance
root = tk.Tk()
root.title("RetroArch Rom Manager v20251211")
root.geometry("1200x800")

# 슈퍼마리오 스타일 테마 적용
style = ttk.Style()
retroTheme.apply_mario_theme(root, style)

# 현재 디렉토리의 리소스 디렉토리에서 아이콘과 기본 이미지를 읽어온다.
baseImage = Image.open("./resources/base.png")
baseImageTk = ImageTk.PhotoImage(baseImage)
ico = Image.open("./resources/icon16.png")
photo = ImageTk.PhotoImage(ico)

# 작업 디렉토리를 변경한다.
fileUtil.changeRootDir()

def subRomDirBoxHandler(event):
    '''
    롬 폴더 콤보 박스에서 폴더를 선택하면 해당 폴더의 롬 리스트를 보여준다.
    이미지가 없을 경우 빨간색으로 표시한다.
    없는 이미지는 가장 유사한 이미지 이름을 찾아서 보여준다.
    '''    
    global mBox, lastSubRomDir, lastRomIdx
    
    romDir = subRomDirBox.get()
    readRom = True

    # 롬 디렉토리가 변경되면 자동으로 이벤트가 발생되기 때문에 강제로 이벤트를 호출하지 않는다.
    if romDir != lastSubRomDir:
        lastSubRomDir = romDir
        lastRomIdx = 0
        readRom = False
        
    fileUtil.changeSubRomDir(romDir)
    xmlListManager = xmlUtil.XmlManager()    
    xmlListManager.readGamesFromXml()    

    if xmlListManager.tree == None:
        mBox.showerror("XML 파일 없음", f"{romDir}에 XML 파일이 없습니다. 폴더를 확인하고 환경 설정을 다시 해 주세요.")
        return
    
    import scrapper
    scrapper.updateXMLFromScrapper(dryRun=False)
    
    # 롬리스트박스와 메시지 박스를 초기화한다.
    romListBox.delete(0, tk.END)        
    msgTextBox.delete(1.0, tk.END)
    
    imgFound = 0
    imgMissCount = 0    

    for game in xmlListManager.gameList:
        from os import path
        romName = game['name']
        romListBox.insert(tk.END, romName)
        
        if not os.path.isfile(game['image']):
            if imgMissCount == 0:
                msgTextBox.insert(tk.INSERT, "=== 존재하지 않는 이미지 목록 ===\n\n")
            
            romListBox.itemconfig(tk.END, {'bg':'red'})
            msgTextBox.insert(tk.INSERT, game['image'] + "\n")      
            imgMissCount += 1
        else:
            imgFound += 1

    if imgMissCount == 0:
        msgTextBox.insert(tk.INSERT,"총 {}개의 롬의 모든 이미지가 정상적으로 존재합니다.".format(imgFound))
    else:           
        msgTextBox.insert(tk.INSERT,"\n총 {}개의 롬 중 {}개의 이미지가 존재하지 않습니다.".format(imgFound + imgMissCount, imgMissCount))

    romListBox.select_set(lastRomIdx)  

    # 롬리스트 박스의 길이가 긴 경우 스크롤을 추가한다.
    if len(xmlListManager.gameList) > 20:
        romListBox.config(height=20)
    
    # 롬 디렉토리가 변경된 경우에만 강제로 롬 선택 핸들러를 호출한다.
    if readRom:
        romListBox.event_generate("<<ListboxSelect>>")    

def romListBoxSelectHandler(event):
    '''
    롬 선택시 이미지 미리 보기를 실행하는 핸들러
    event: tkinter의 이벤트 객체
    '''

    global lastRomIdx

    xmlManager = xmlUtil.XmlManager()
    
    # 포커스를 잃을 경우 에러가 나는 문제 해결을 위한 코드
    if len(romListBox.curselection()) == 0: return
    
    lastRomIdx = romListBox.curselection()[0]    
    romListBox.see(lastRomIdx)
    game = xmlManager.findGameByIdx(lastRomIdx)
    imagePath = game['image']
    
    print("롬파일 정보 읽기: ", game['path']) 

    # 이미지를 미리 보여준다.
    import imgUtil        
    imageTk = imgUtil.findImage(imagePath)    

    if len(imagePath) > 20:
        imagePath = imagePath[:20] + "..."

    if (imageTk != None):
        imgLabel.configure(image=imageTk)
        imgLabel.image = imageTk
    else:
        imgLabel.configure(image=baseImageTk, width=500)    

    # 롬의 세부 정보를 보여준다.
    romTitleEntry.delete(0, tk.END)
    romTitleEntry.insert(0, game['name'])
    romPathEntry.delete(0, tk.END)
    romPathEntry.insert(0, game['path'])
    romImageEntry.delete(0, tk.END)
    romImageEntry.insert(0, game['image'])
    romRatingEntry.delete(0, tk.END)
    romRatingEntry.insert(0, game['rating'])
    romDescriptionText.delete(1.0, tk.END)
    romDescriptionText.insert(1.0, game['desc'])

def deleteRomAndImageHandler():
    '''
    선택된 롬과 이미지를 삭제하는 핸들러
    '''
    
    global lastRomIdx
    # 먼저 파일과 이미지를 삭제한다.    
    xmlManager = xmlUtil.XmlManager()
    game = xmlManager.findGameByIdx(lastRomIdx)
    fileUtil.deleteRomAndImages(game)

    #XML에서 해당 목록을 제거한다.
    xmlManager.remove(game)
    lastRomIdx = 0
    
    # 롬 리스트를 다시 읽어서 보여준다.
    subRomDirBox.event_generate("<<ComboboxSelected>>")

def exportGroovyList():
    '''
    그루비용 리스트를 내보내는 핸들러
    '''
    import groovy
    from syncFile import SyncFile
    syncFile = SyncFile()
    syncFile.setServerInfo("groovy")
    status = syncFile.connectSSH()
    if not status:
        mBox.showerror("SSH 연결 실패", "SSH 연결에 실패했습니다. 설정을 확인해 주세요.")
        return
    syncFile.copyRemoteList()
    match, total = groovy.exportGroovyList()    
    syncFile.exportLocalList()
    # 성공 메시지 출력
    mBox.showinfo("그루비 리스트 내보내기", f"그루비 리스트 {match}개를 변환해서 {syncFile.remotePath}로 내보냈습니다.\n")

def exportRomsToGroovy():
    '''
    현재 폴더의 롬 파일과 이미지를 서버와 동기화하는 핸들러
    '''
    import groovy
    from syncFile import SyncFile
    syncFile = SyncFile()
    syncFile.setServerInfo("groovy")
    
    # 작은 상태창 생성
    statusWindow = tk.Toplevel()
    statusWindow.title("그루비 동기화")
    statusWindow.geometry("300x100")
    # 상태창 위치를 메인 윈도우 중앙으로 설정
    x = root.winfo_x() + (root.winfo_width() // 2) - 150
    y = root.winfo_y() + (root.winfo_height() // 2) - 50
    statusWindow.geometry(f"+{x}+{y}")
    retroTheme.apply_toplevel_style(statusWindow)

    # 상태 메시지 라벨
    statusLabel = ttk.Label(statusWindow, text="그루비 서버에 접속중...")
    statusLabel.pack(pady=20)

    # 프로그레스 바 추가
    progressBar = ttk.Progressbar(statusWindow, length=200, mode='determinate')
    progressBar.pack(pady=10)
    progressBar['value'] = 0
    
    # 상태창 업데이트
    statusWindow.update()

    status = syncFile.connectSSH()
    if not status:
        # 상태창 닫기
        statusWindow.destroy()
        mBox.showerror("SSH 연결 실패", "SSH 연결에 실패했습니다. 설정을 확인해 주세요.")
        return
    
    statusLabel.config(text="그루비 서버에 접속 성공.")    
    statusWindow.update()
    # 0.5 초 정도 슬립?
    import time
    time.sleep(1)
    
    statusLabel.config(text=f"그루비와 {lastSubRomDir} 동기화 중...")
    
    # match = 100
    syncStatus = syncFile.syncSubRoms(lastSubRomDir, statusWindow, statusLabel, progressBar)
    
    # 성공 메시지 출력
    # 상태창 닫기
    statusLabel.config(text="동기화 완료!")
    progressBar['value'] = 100
    statusWindow.update()
    time.sleep(1)
    statusWindow.destroy()    
    mBox.showinfo("그루비 리스트 내보내기", f" {lastSubRomDir} 폴더의 롬 {syncStatus[2]}개를 복사했습니다.\n")


def openImageScrapWindow():
    '''
    이미지 스크랩 서브 윈도우를 열어주는 핸들러
    현재 선택된 게임의 이미지를 ScreenScraper API로 검색하고 다운로드
    '''
    global lastRomIdx, lastSubRomDir

    import screenScraper
    from screenScraper import ScreenScraperAPI, getSystemId

    # 현재 선택된 게임 정보 가져오기
    xmlManager = xmlUtil.XmlManager()
    game = xmlManager.findGameByIdx(lastRomIdx)

    # 서브 윈도우 생성
    scrapWindow = tk.Toplevel()
    scrapWindow.title("이미지 스크랩")
    scrapWindow.geometry("600x500")
    x = root.winfo_x() + (root.winfo_width() // 2) - 300
    y = root.winfo_y() + (root.winfo_height() // 2) - 250
    scrapWindow.geometry(f"+{x}+{y}")
    retroTheme.apply_toplevel_style(scrapWindow)

    # 메인 프레임
    mainFrame = ttk.Frame(scrapWindow, padding=10)
    mainFrame.pack(fill='both', expand=True)

    # 게임 정보 표시
    infoFrame = ttk.Frame(mainFrame)
    infoFrame.pack(fill='x', pady=5)

    ttk.Label(infoFrame, text="게임 이름:").grid(row=0, column=0, sticky='e', padx=5)
    ttk.Label(infoFrame, text=game['name']).grid(row=0, column=1, sticky='w', padx=5)

    ttk.Label(infoFrame, text="ROM 파일:").grid(row=1, column=0, sticky='e', padx=5)
    ttk.Label(infoFrame, text=game['path']).grid(row=1, column=1, sticky='w', padx=5)

    ttk.Label(infoFrame, text="시스템:").grid(row=2, column=0, sticky='e', padx=5)
    systemId = getSystemId(lastSubRomDir)
    ttk.Label(infoFrame, text=f"{lastSubRomDir} (ID: {systemId})").grid(row=2, column=1, sticky='w', padx=5)

    # 구분선
    ttk.Separator(mainFrame, orient='horizontal').pack(fill='x', pady=10)

    # 상태 표시 영역
    statusFrame = ttk.Frame(mainFrame)
    statusFrame.pack(fill='both', expand=True, pady=5)

    statusText = scrolledtext.ScrolledText(statusFrame, width=70, height=15)
    retroTheme.apply_text_style(statusText)
    statusText.pack(fill='both', expand=True)

    # 이미지 미리보기 라벨
    previewLabel = ttk.Label(mainFrame, text="이미지 미리보기")
    previewLabel.pack(pady=5)

    # 버튼 프레임
    buttonFrame2 = ttk.Frame(mainFrame)
    buttonFrame2.pack(fill='x', pady=10)

    def logStatus(message):
        statusText.insert(tk.END, message + "\n")
        statusText.see(tk.END)
        scrapWindow.update()

    def doScrap():
        """스크랩 실행"""
        api = ScreenScraperAPI()

        if not api.isConfigured():
            logStatus("오류: ScreenScraper 계정이 설정되지 않았습니다.")
            logStatus("secret.ini 파일에 다음 항목을 추가하세요:")
            logStatus("  ScreenScraperID = 계정ID")
            logStatus("  ScreenScraperPassword = 비밀번호")
            return

        if systemId is None:
            logStatus(f"오류: '{lastSubRomDir}' 시스템의 ID를 찾을 수 없습니다.")
            return

        romFullPath = os.path.join(os.getcwd(), game['path'])
        romName = os.path.basename(game['path'])

        logStatus(f"검색 중: {romName}")
        logStatus(f"시스템 ID: {systemId}")

        # 게임 검색
        gameData = api.searchGame(romFullPath, systemId, romName)

        if gameData is None:
            logStatus("게임을 찾을 수 없습니다.")
            return

        # 게임 정보 표시
        gameInfo = api.getGameInfo(gameData, lang='ko')
        logStatus(f"\n=== 검색 결과 ===")
        logStatus(f"게임 이름: {gameInfo.get('name', 'N/A')}")
        logStatus(f"개발사: {gameInfo.get('developer', 'N/A')}")
        logStatus(f"퍼블리셔: {gameInfo.get('publisher', 'N/A')}")
        logStatus(f"장르: {gameInfo.get('genre', 'N/A')}")
        logStatus(f"출시일: {gameInfo.get('releasedate', 'N/A')}")

        # 이미지 URL 추출
        images = api.getGameImages(gameData)
        logStatus(f"\n=== 사용 가능한 이미지 ===")
        for imgType, url in images.items():
            logStatus(f"  {imgType}: {url[:50]}...")

        # 이미지 다운로드 (ss = 스크린샷)
        if 'ss' in images:
            # 저장 경로 설정
            imageDir = os.path.dirname(game['image'])
            if not imageDir:
                imageDir = './media/images'
            imageName = os.path.splitext(os.path.basename(game['path']))[0] + '.png'
            savePath = os.path.join(os.getcwd(), imageDir, imageName)

            logStatus(f"\n이미지 다운로드 중: {savePath}")

            if api.downloadImage(images['ss'], savePath):
                logStatus("이미지 다운로드 완료!")

                # XML 업데이트
                game['image'] = os.path.join(imageDir, imageName).replace('\\', '/')
                xmlManager.updateGame(game['path'], game)
                logStatus("XML 업데이트 완료!")
            else:
                logStatus("이미지 다운로드 실패")
        else:
            logStatus("\n스크린샷 이미지가 없습니다.")

        # 박스 아트 다운로드
        if 'box-2D' in images:
            imageDir = os.path.dirname(game['image']) if game['image'] else './media/images'
            boxName = os.path.splitext(os.path.basename(game['path']))[0] + '_box.png'
            boxPath = os.path.join(os.getcwd(), imageDir, boxName)

            logStatus(f"\n박스 아트 다운로드 중: {boxPath}")
            if api.downloadImage(images['box-2D'], boxPath):
                logStatus("박스 아트 다운로드 완료!")

    def doScrapInfo():
        """게임 정보만 스크랩 (이미지 제외)"""
        api = ScreenScraperAPI()

        if not api.isConfigured():
            logStatus("오류: ScreenScraper 계정이 설정되지 않았습니다.")
            return

        if systemId is None:
            logStatus(f"오류: '{lastSubRomDir}' 시스템의 ID를 찾을 수 없습니다.")
            return

        romFullPath = os.path.join(os.getcwd(), game['path'])
        romName = os.path.basename(game['path'])

        logStatus(f"게임 정보 검색 중: {romName}")

        gameData = api.searchGame(romFullPath, systemId, romName)

        if gameData is None:
            logStatus("게임을 찾을 수 없습니다.")
            return

        gameInfo = api.getGameInfo(gameData, lang='ko')

        logStatus(f"\n=== 게임 정보 ===")
        logStatus(f"이름: {gameInfo.get('name', 'N/A')}")
        logStatus(f"설명: {gameInfo.get('description', 'N/A')[:200]}...")
        logStatus(f"개발사: {gameInfo.get('developer', 'N/A')}")
        logStatus(f"퍼블리셔: {gameInfo.get('publisher', 'N/A')}")
        logStatus(f"장르: {gameInfo.get('genre', 'N/A')}")

        # 게임 정보 업데이트 확인
        result = mBox.askquestion("정보 업데이트", "검색된 정보로 게임 정보를 업데이트하시겠습니까?")
        if result == 'yes':
            if gameInfo.get('name'):
                game['name'] = gameInfo['name']
            if gameInfo.get('description'):
                game['desc'] = gameInfo['description']
            xmlManager.updateGame(game['path'], game)
            logStatus("\n게임 정보가 업데이트되었습니다!")

    # 버튼들
    scrapButton = ttk.Button(buttonFrame2, text="이미지 스크랩", command=doScrap, style='Green.TButton')
    scrapButton.pack(side='left', padx=5)

    infoButton = ttk.Button(buttonFrame2, text="정보만 검색", command=doScrapInfo, style='Blue.TButton')
    infoButton.pack(side='left', padx=5)

    closeButton = ttk.Button(buttonFrame2, text="닫기", command=scrapWindow.destroy)
    closeButton.pack(side='right', padx=5)


########################
# 중첩 프레임          #
########################

# 그리드 설정 - 열과 행의 비율 조정
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
root.grid_columnconfigure(2, weight=0)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)

# 타이틀 프레임 (상단 전체)
titleFrame = ttk.Frame(root)
titleFrame.grid(column=0, row=0, columnspan=3, pady=10, padx=10, sticky='ew')

# 롬 리스트 프레임 (좌측 상단)
romListFrame = ttk.Frame(root)
romListFrame.grid(column=0, row=1, pady=5, padx=10, sticky='nsew')

# 이미지 미리보기 프레임 (중앙 상단)
imagePreviewFrame = ttk.Frame(root)
imagePreviewFrame.grid(column=1, row=1, pady=5, padx=5, sticky='n')

# 기본 버튼 프레임 (우측 상단)
buttonFrame = ttk.Frame(root)
buttonFrame.grid(column=2, row=1, pady=5, padx=10, sticky='n')

# 메시지용 프레임 (좌측 하단)
outputMessageFrame = ttk.Frame(root)
outputMessageFrame.grid(column=0, row=2, pady=5, padx=10, sticky='nsew')

# 롬 세부 정보 프레임 (중앙 하단)
detailedRomInfoFrame = ttk.Frame(root)
detailedRomInfoFrame.grid(column=1, row=2, pady=5, padx=5, sticky='nsew')

# 설정 버튼 프레임 (우측 하단)
settingFrame = ttk.Frame(root)
settingFrame.grid(column=2, row=2, pady=5, padx=10, sticky='n')


# 타이틀 프레임 중앙 정렬
titleFrame.grid_columnconfigure(0, weight=1)
titleFrame.grid_columnconfigure(4, weight=1)

# 앱 타이틀
appTitle = ttk.Label(titleFrame, text="RetroArch Rom Manager", style='Title.TLabel')
appTitle.grid(column=1, row=0, columnspan=3, pady=(0, 10))

# 롬 폴더 선택 프레임
label = ttk.Label(titleFrame, text="롬 폴더:")
label.grid(column=1, row=1, pady=5, padx=5, sticky='e')

# 서브 롬 폴더 콤보 박스
basePath = config.getBasePath()
subDirs = fileUtil.readSubDirs()

while len(subDirs) == 0:
    # 서브 롬 폴더가 없을 경우 파일 다이얼로그를 열어서 폴더를 선택하도록 한다.
    # 폴더 선택 후 다시 서브 롬 폴더를 읽어온다.
    
    # 오류 메시지 표시
    mBox.showerror("서브 롬 폴더 없음", "기본 폴더에 서브 롬 폴더가 없습니다. 기본 폴더를 다시 선택해 주세요.")
    from tkinter import filedialog    
    basePath = filedialog.askdirectory(initialdir=config.getBasePath())    
    os.chdir(basePath)
    subDirs = fileUtil.readSubDirs()

    # 설정 업데이트
    config.setBasePath(basePath)    

subRomDirBox = ttk.Combobox(titleFrame, values=subDirs, width=30)

subRomDirBox.grid(column=2, row=1, padx=5, pady=5)
subRomDirBox.bind("<<ComboboxSelected>>", subRomDirBoxHandler)

# 새로고침 버튼
refreshButton = ttk.Button(titleFrame, text="새로고침", command=lambda: subRomDirBox.event_generate("<<ComboboxSelected>>"))
refreshButton.grid(column=3, row=1, pady=5, padx=5)

# 롬 리스트
label2 = ttk.Label(romListFrame, text="롬 리스트")
label2.grid(column=0, row=0, pady=5, padx=5, sticky='w')
from tkinter import Listbox
romListBox = Listbox(romListFrame)
romListBox.config(height=20, width=45)
retroTheme.apply_listbox_style(romListBox)
romListBox.bind('<<ListboxSelect>>', romListBoxSelectHandler)
romListBox.grid(column=0, row=1, padx=5, pady=5, sticky='nsew')

# 롬 세부 정보
romDescriptionLabel = ttk.Label(detailedRomInfoFrame, text="롬 세부 정보")
romDescriptionLabel.grid(column=0, row=0, pady=5, padx=5, sticky='w', columnspan=4)

# 롬 제목
romTitleLabel = ttk.Label(detailedRomInfoFrame, text="롬 이름")
romTitleLabel.grid(column=0, row=1, pady=2, padx=5, sticky='e')
romTitleEntry = ttk.Entry(detailedRomInfoFrame, width=45)
romTitleEntry.grid(column=1, row=1, pady=2, padx=5, columnspan=3, sticky='w')

# 롬 경로
romPathLabel = ttk.Label(detailedRomInfoFrame, text="롬 경로")
romPathLabel.grid(column=0, row=2, pady=2, padx=5, sticky='e')
romPathEntry = ttk.Entry(detailedRomInfoFrame, width=45)
romPathEntry.grid(column=1, row=2, pady=2, padx=5, columnspan=3, sticky='w')

# 이미지 경로
romImageLabel = ttk.Label(detailedRomInfoFrame, text="이미지 경로")
romImageLabel.grid(column=0, row=3, pady=2, padx=5, sticky='e')
romImageEntry = ttk.Entry(detailedRomInfoFrame, width=45)
romImageEntry.grid(column=1, row=3, pady=2, padx=5, columnspan=3, sticky='w')

# Rating
romRatingLabel = ttk.Label(detailedRomInfoFrame, text="Rating")
romRatingLabel.grid(column=0, row=4, pady=2, padx=5, sticky='e')
romRatingEntry = ttk.Entry(detailedRomInfoFrame, width=45)
romRatingEntry.grid(column=1, row=4, pady=2, padx=5, columnspan=3, sticky='w')

# 세부 정보
romDescLabel2 = ttk.Label(detailedRomInfoFrame, text="세부 정보")
romDescLabel2.grid(column=0, row=5, pady=2, padx=5, sticky='ne')
romDescriptionText = scrolledtext.ScrolledText(detailedRomInfoFrame, width=45, height=5)
retroTheme.apply_text_style(romDescriptionText)
romDescriptionText.grid(column=1, row=5, columnspan=3, pady=2, padx=5, sticky='w')

# 롬 정보 업데이트 버튼
def updateRomInfoHandler():
    '''
    롬 정보를 업데이트하는 핸들러
    '''
    global lastRomIdx

    # 롬 선택 핸들러 코드를 참고할 것 
    # 롬 정보를 수정하면 롬리스트가 포커스를 잃어버리기 때문에 미리 lastRomIdx를 저장해 두었다.    
    xmlManager = xmlUtil.XmlManager()
    game = xmlManager.findGameByIdx(lastRomIdx)
    oldPath = game['path']

    # 새로운 다이얼로그를 열어 정말 저장 할 건지 물어본다.
    romInfo = '''롬 이름: {}
    롬 경로: {}
    롬 Rating: {}
    이미지 경로: {}    
    세부 정보: {}'''.format(romTitleEntry.get(), romPathEntry.get(), romRatingEntry.get(), romImageEntry.get(), romDescriptionText.get(1.0, tk.END))
    result = mBox.askquestion("롬 정보 업데이트", "{} 롬 정보를 업데이트 하시겠습니까?".format(romInfo))
    if result == 'yes':        
        game['name'] = romTitleEntry.get()
        game['path'] = romPathEntry.get()
        game['rating'] = romRatingEntry.get()
        game['image'] = romImageEntry.get()
        game['desc'] = romDescriptionText.get(1.0, tk.END)
        lastRomIdx = xmlManager.updateGame(oldPath, game)    
        print("인덱스 업데이트:", lastRomIdx)
        subRomDirBox.event_generate("<<ComboboxSelected>>")

romUpdateButton = ttk.Button(detailedRomInfoFrame, text="롬 정보 업데이트", command=updateRomInfoHandler, style='Blue.TButton')
romUpdateButton.grid(column=1, row=6, pady=8, padx=5, sticky='e')

def translateGameInfoHandler():
    global lastRomIdx, romTable
    xmlManager = xmlUtil.XmlManager()
    game = xmlManager.findGameByIdx(lastRomIdx)
    filename = game['path']
    
    translate.translateGameInfo(game)
    romTitleEntry.delete(0, tk.END)
    romTitleEntry.insert(0, game['name'])
    romDescriptionText.delete(1.0, tk.END)
    romDescriptionText.insert(1.0, game['desc'])
    lastRomIdx = xmlManager.updateGame(filename, game)
    print("인덱스 업데이트:", lastRomIdx)
    subRomDirBox.event_generate("<<ComboboxSelected>>")

translateGameInfoButton = ttk.Button(detailedRomInfoFrame, text="롬 정보 번역하기", command=translateGameInfoHandler, style='Yellow.TButton')
translateGameInfoButton.grid(column=2, row=6, pady=8, padx=5, columnspan=2, sticky='w')


# 출력 메시지
label3 = ttk.Label(outputMessageFrame, text="출력 메시지")
label3.grid(column=0, row=0, pady=5, padx=5, sticky='w')
# 메시지 출력용 텍스트 박스
msgTextBox = Text(outputMessageFrame)
msgTextBox.config(height=15, width=45)
retroTheme.apply_text_style(msgTextBox)
msgTextBox.grid(column=0, row=1, padx=5, pady=5, sticky='nsew')


# 이미지 미리보기 라벨
imgLabel = ttk.Label(imagePreviewFrame, image=baseImageTk)
imgLabel.grid(column=0, row=1, pady=5, padx=5)

#######################################
# buttons                             #
#######################################

# 버튼 공통 너비
BTN_WIDTH = 20

# 기본 동작 라벨
actionLabel = ttk.Label(buttonFrame, text="기본 동작")
actionLabel.grid(column=0, row=0, pady=(0, 5), padx=5, sticky='w')

# 선택 롬 실행 버튼
import mainHandler
import asyncio

runRomButton = ttk.Button(buttonFrame, text="선택 롬 실행", width=BTN_WIDTH,
                          command=lambda: asyncio.run(mainHandler.runRetroarch(subRomDirBox.get(), xmlUtil.XmlManager().findGameByIdx(lastRomIdx)['path'],config)),
                          style='Green.TButton')
runRomButton.grid(column=0, row=1, pady=3, padx=5, sticky='ew')

def openFolderHandler(folderPath):
    '''
    기기 폴더를 열어주는 핸들러
    '''
    if path.exists(folderPath) and path.isdir(folderPath):
        os.startfile(folderPath)
    else:
        mBox.showerror("폴더 없음", folderPath + " 가 없습니다. 폴더를 확인해 주세요.")

# 롬 폴더 열기 버튼
romFolderOpenButton = ttk.Button(buttonFrame, text="롬 폴더 열기", width=BTN_WIDTH,
                                  command=lambda: openFolderHandler(os.getcwd()))
romFolderOpenButton.grid(column=0, row=2, pady=3, padx=5, sticky='ew')

# 이미지 폴더 열기 버튼
imgFolderOpenButton = ttk.Button(buttonFrame, text="이미지 폴더 열기", width=BTN_WIDTH,
                                  command=lambda: openFolderHandler(path.join(os.getcwd(), path.dirname(xmlUtil.XmlManager().findGameByIdx(lastRomIdx)['image']))))
imgFolderOpenButton.grid(column=0, row=3, pady=3, padx=5, sticky='ew')

# 이미지 스크랩 버튼
imgScrapButton = ttk.Button(buttonFrame, text="이미지 스크랩", width=BTN_WIDTH,
                             command=openImageScrapWindow, style='Blue.TButton')
imgScrapButton.grid(column=0, row=4, pady=3, padx=5, sticky='ew')

# 롬 파일 및 이미지 삭제 버튼
fileDeleteButton = ttk.Button(buttonFrame, text="선택 롬/이미지 삭제", width=BTN_WIDTH,
                               command=deleteRomAndImageHandler, style='Danger.TButton')
fileDeleteButton.grid(column=0, row=5, pady=3, padx=5, sticky='ew')

# 구분선
ttk.Separator(buttonFrame, orient='horizontal').grid(column=0, row=6, pady=10, padx=5, sticky='ew')

# 그루비 라벨
groovyLabel = ttk.Label(buttonFrame, text="그루비 동기화")
groovyLabel.grid(column=0, row=7, pady=(0, 5), padx=5, sticky='w')

# 그루비 리스트 내보내기 버튼
groovyListButton = ttk.Button(buttonFrame, text="리스트 내보내기", width=BTN_WIDTH,
                               command=exportGroovyList)
groovyListButton.grid(column=0, row=8, pady=3, padx=5, sticky='ew')

# 그루비로 롬 동기화 버튼
groovySyncButton = ttk.Button(buttonFrame, text="롬 동기화", width=BTN_WIDTH,
                               command=exportRomsToGroovy, style='Green.TButton')
groovySyncButton.grid(column=0, row=9, pady=3, padx=5, sticky='ew')


def setBasePath():
    '''
    파일 다이얼로그를 열어 기본 폴더를 설정한다.
    기본 폴더는 서브 롬 폴더가 있어야 하며 잘못 선택할 경우 다시 선택하도록 한다.
    '''
    from tkinter import filedialog

    subDirs = []
    while True:   
        basePath = filedialog.askdirectory(initialdir=config.getBasePath())    
        os.chdir(basePath)
        subDirs = fileUtil.readSubDirs()
        if len(subDirs) != 0: 
            break
        mBox.showerror("서브 롬 폴더 없음", "서브 롬 폴더가 없습니다. 폴더를 다시 선택해 주세요.")   
    
    config.setBasePath(basePath)
    config.setLastRomDir(subDirs[0])
    config.save()
    return subDirs

# 기본 폴더 재설정 버튼
def setBasePathHandler():
    '''
    기본 폴더를 재설정하는 핸들러
    '''    
    subRomDirBox['values'] = fileUtil.setBasePath()
    subRomDirBox.set(status.getLastSubRomDirectory())
    subRomDirBox.event_generate("<<ComboboxSelected>>")

# 설정 라벨
settingLabel = ttk.Label(settingFrame, text="설정")
settingLabel.grid(column=0, row=0, pady=(0, 5), padx=5, sticky='w')

setBasePathButton = ttk.Button(settingFrame, text="기본 폴더 재설정", width=BTN_WIDTH,
                                command=setBasePathHandler)
setBasePathButton.grid(column=0, row=1, pady=3, padx=5, sticky='ew')

# 기기 폴더 재설정 버튼
def setTargetPathHandler():
    '''
    기기 폴더를 재설정하는 핸들러
    '''
    from tkinter import filedialog
    targetPath = filedialog.askdirectory(initialdir=config.getTargetPath())
    config.setTargetPath(targetPath)
    config.save()

setTargetPathButton = ttk.Button(settingFrame, text="기기 폴더 재설정", width=BTN_WIDTH,
                                  command=setTargetPathHandler)
setTargetPathButton.grid(column=0, row=2, pady=3, padx=5, sticky='ew')

# 마지막으로 선택된 폴더의 롬 리스트를 보여줌
if not status.getLastSubRomDirectory() in subRomDirBox['values']:
    status.setLastSubRomDirectory(subRomDirBox['values'][0])
subRomDirBox.set(status.getLastSubRomDirectory())
subRomDirBox.event_generate("<<ComboboxSelected>>")

# 설정 파일 열기 버튼
openConfigButton = ttk.Button(settingFrame, text="설정 파일 열기", width=BTN_WIDTH,
                               command=lambda: os.startfile(config.getConfigFilePath()))
openConfigButton.grid(column=0, row=3, pady=3, padx=5, sticky='ew')

# RetroArch 폴더 열기 버튼
retroarchFolderOpenButton = ttk.Button(settingFrame, text="RetroArch 폴더 열기", width=BTN_WIDTH,
                                        command=lambda: openFolderHandler(path.dirname(config.getRetroarchPath())))
retroarchFolderOpenButton.grid(column=0, row=4, pady=3, padx=5, sticky='ew')

# Scrapper 실행 버튼
runScrapperButton = ttk.Button(settingFrame, text="Scrapper 실행", width=BTN_WIDTH,
                                command=lambda: asyncio.run(mainHandler.runScrapper(config)), style='Green.TButton')
runScrapperButton.grid(column=0, row=5, pady=3, padx=5, sticky='ew')


# ScrapXML 삭제 버튼
def deleteFile(filePath):
    # yn 다이얼로그를 열고 한 번 더 물어본다.
    result = mBox.askquestion("ScrapXML 삭제", f"ScrapXML 파일 {filePath}을 삭제하시겠습니까?")    
    if not result:
        mBox.showinfo("ScrapXML 삭제", "ScrapXML 파일을 삭제를 취소합니다.")
        return
    if path.isfile(filePath):
        os.remove(filePath)
        mBox.showinfo("ScrapXML 삭제", "ScrapXML 파일을 삭제했습니다.")
    else:
        mBox.showinfo("ScrapXML 삭제", "ScrapXML 파일이 없습니다.")

scraperXmlDeleteButton = ttk.Button(settingFrame, text="ScrapXML 삭제", width=BTN_WIDTH,
                                    command=lambda: deleteFile(config.getScrapperXmlName()),
                                    style='Danger.TButton')
scraperXmlDeleteButton.grid(column=0, row=6, pady=3, padx=5, sticky='ew')

# 종료시 설정을 저장한다.
def onClosing():
    print("메인 프로그램 종료")
    status.setLastRomIdx(lastRomIdx)
    status.setLastSubRomDirectory(subRomDirBox.get())    
    status.save()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", onClosing)

# 애플리케이션을 실행합니다.
root.wm_iconphoto(False, photo)
root.mainloop()
