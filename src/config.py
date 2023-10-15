import json
import os
from os import path

class Config:
    '''
    환경 설정을 담당하는 클래스
    환결 설정은 config.json 파일에 저장된다.
    '''

    def __init__(self):
        # setup 윈도우에서 저장하기를 누를 때 기본 폴더가 변경되어 발생하는 오류를 막기위해 현재 폴더를 기본 폴더로 설정한다.
        self.jsonFileName = path.join(os.getcwd(), 'config.json')
        self.load()

    def load(self):
        '''
        환경 설정 파일을 읽어서 객체에 저장한다.
        '''
        self.configJson = json.load(open(self.jsonFileName, 'r+'))
    
    def save(self):
        '''
        환경 설정 파일을 저장한다.
        '''
        json.dump(self.configJson, open(self.jsonFileName, 'w+'), indent=4)
    
    def getBasePath(self):
        '''
        기본 경로를 반환한다.
        '''
        return self.configJson['basePath']
    
    def setBasePath(self, basePath):
        '''
        기본 경로를 설정한다.
        '''
        self.configJson['basePath'] = basePath

    def getTargetPath(self):
        '''
        대상 경로를 반환한다.
        '''
        return self.configJson['targetPath']
    
    def setTargetPath(self, targetPath):
        '''
        대상 경로를 설정한다.
        '''
        self.configJson['targetPath'] = targetPath

    def getExtension(self):
        '''
        확장자를 반환한다.
        '''
        return self.configJson['extension']   

    def getXmlName(self):
        '''
        xml 파일명을 반환한다.
        '''
        return self.configJson['xmlName']
    
    def getLastRomDir(self):
        '''
        마지막으로 선택한 rom 경로를 반환한다.
        '''
        return self.configJson['lastSubRomDirectory']
    
    def setLastRomDir(self, lastRomDir):
        '''
        마지막으로 선택한 rom 경로를 설정한다.
        '''
        self.configJson['lastSubRomDirectory'] = lastRomDir      

    def getRetroarchPath(self):
        '''
        retroarch 경로를 반환한다.
        '''
        return self.configJson['retroarchPath']   
    
    def getCoreLibaryName(self, subRomDir):
        '''
        core libary 이름을 반환한다.
        '''
        return self.configJson['cores'][subRomDir]

        

# main function for test

if __name__ == "__main__":
    cfg = Config()
    print("Base Path: ", cfg.getBasePath())
    print("Target Path: ", cfg.getTargetPath())
    print("Extension: ", cfg.getExtension())
    print("Xml Name: ", cfg.getXmlName())
    print("Last Rom Dir: ", cfg.getLastRomDir())
    print("Retroarch Path: ", cfg.getRetroarchPath())
    print("Core Libary Name: ", cfg.getCoreLibaryName("gb"))
    cfg.save()