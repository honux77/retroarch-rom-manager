# 핸들러를 제외한 나머지 함수들을 모아놓은 파일입니다.
# 각 함수들은 main.py에서 호출되어 사용됩니다.
import os


def initMainProgram(cfg):
    '''메인 윈도우 시작시 실행되는 초기화 루틴'''
    cleanRomFolder(cfg)


def cleanRomFolder(cfg):
    '''롬 폴더 하위의 media/manual 폴더 안의 파일을 삭제하고 폴더도 삭제'''
    import shutil
    romBasePath = cfg.getBasePath()
    for subDir in os.listdir(romBasePath):
        manualPath = os.path.join(romBasePath, subDir, 'media', 'manual')
        if os.path.exists(manualPath):
            print(f"Removing manual folder: {manualPath}")
            shutil.rmtree(manualPath)



async def runRetroarch(subRomDir, romPath, cfg):
    '''Retroarch를 실행합니다.'''
    from os import path
    import subprocess
    cmd = [cfg.getRetroarchPath(), '-L', cfg.getCoreLibaryName(subRomDir), romPath]        
    print("에뮬레이터를 실행합니다: ", cmd)
    subprocess.Popen(cmd)


async def runScrapper(cfg):
    '''스크래퍼를 실행합니다.'''
    from os import path
    import subprocess
    cmd = [cfg.getScrapperPath()]
    print("스크래퍼를 실행합니다: ", cmd)
    subprocess.Popen(cmd)


# maninFunc test code
if __name__ == "__main__":
    import os
    from config import Config
    cfg = Config()
    os.chdir(cfg.getBasePath())
    print("Current Path: ", os.getcwd())
    runRetroarch("gb", "./Bonk's Adventure (USA).zip", cfg)