# 핸들러를 제외한 나머지 함수들을 모아놓은 파일입니다.
# 각 함수들은 main.py에서 호출되어 사용됩니다.
import os

async def runRetroarch(subRomDir, romPath, cfg):
    '''Retroarch를 실행합니다.'''
    from os import path
    import subprocess
    cmd = [cfg.getRetroarchPath(), '-L', cfg.getCoreLibaryName(subRomDir), path.join(subRomDir,romPath)]        
    print("에뮬레이터를 실행합니다: ", cmd)
    subprocess.Popen(cmd)


async def runScrapper(cfg):
    '''스크래퍼를 실행합니다.'''
    from os import path
    import subprocess
    cmd = [cfg.getScrapperPath()]
    print("스크래퍼를 실행합니다: ", cmd)
    subprocess.Popen(cmd)

# test

if __name__ == "__main__":
    import os
    from config import Config
    cfg = Config()
    os.chdir(cfg.getBasePath())
    print("Current Path: ", os.getcwd())
    runRetroarch("gb", "./Bonk's Adventure (USA).zip", cfg)