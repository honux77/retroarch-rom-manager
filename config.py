import json
import os
from os import path

class Config:
    '''
    환경 설정을 담당하는 클래스
    환결 설정은 config.json 파일에 저장된다.

    config.json 파일의 예시는 다음과 같다.
    {    
    "basePath": "d:\\Retropie\\roms\\",    
    "targetPath": "f:\\",    
    "extension": ["zip", "chd", "dsk"],
    "xmlName" : "gamelist.xml",    
    "baseImageName": "base.png",
    "iconFileName": "icon16.png",
    "lastSubRomDirectory": "gba"
    }
    '''

    def __init__(self):        
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
        json.dump(self.configJson, open(self.jsonFileName, 'w+'))
    
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
