import json
import os
from os import path

from singleton import singleton

@singleton
class Config:
    '''
    환경 설정을 담당하는 싱글톤 클래스
    환결 설정은 config.json 파일에 저장된다.
    '''

    def __init__(self):
        # setup 윈도우에서 저장하기를 누를 때 기본 폴더가 변경되어 발생하는 오류를 막기위해 절대 경로로 파일 위치를 지정정
        print("Load Global Configurations")
        self.jsonFileName = path.join(os.getcwd(), 'config.json')
        print("설정 파일 경로: ", self.jsonFileName)
        self.load()
        self.loadSecretIni()

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

    def getConfigFilePath(self):
        '''
        환경 설정 파일의 경로를 반환한다.
        '''
        return self.jsonFileName;
    
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

    def getExtensions(self):
        '''
        확장자를 반환한다.
        '''
        return self.configJson['extensions']   
    

    def getScrapperXmlName(self):
        '''
        스크래퍼에서 생성된 xml 파일명을 반환한다.
        '''
        return self.configJson['scrapperXmlName']

    def getXmlName(self):
        '''
        xml 파일명을 반환한다.
        '''
        return self.configJson['xmlName']    

    def getRetroarchPath(self):
        '''
        retroarch 경로를 반환한다.
        '''
        return self.configJson['retroarchPath']   
    
    def getRetroarchConfigPath(self):
        '''
        retroarch config 경로를 반환한다.
        '''
        return self.configJson['retroarchConfigPath']
    
    def getCoreLibaryName(self, subRomDir):
        '''
        core libary 이름을 반환한다.
        '''
        return self.configJson['cores'][subRomDir]
    
    def getScrapperPath(self):
        '''
        스크래퍼 경로를 반환한다.
        '''
        return self.configJson['scrapperPath']
    
    def loadSecretIni(self):
        '''ini 파일에서 secret 정보를 읽어온다.'''
        import configparser
        self.secret = configparser.ConfigParser()
        # 절대 경로로 secret.ini 파일 경로 지정 (작업 디렉토리 변경에 영향받지 않도록)
        secretIniPath = path.join(path.dirname(self.jsonFileName), 'secret.ini')
        if path.exists(secretIniPath):
            self.secret.read(secretIniPath)
        else:
            self.secret = None
    
    def getDeepLApiKey(self):
        '''
        DeepL API Key를 반환한다.
        '''
        if self.secret == None:
            return None
        return self.secret['DEFAULT']['DeepLApiKey']    
    
    def getScrapperSkipWord(self):
        '''
        스크래퍼에서 제외할 단어를 반환한다.
        '''
        return self.configJson['scrapperSkipWord']
    
    def getServerInfo(self, serverName):
        return self.configJson[serverName]
    

# main function for test
if __name__ == "__main__":
    cfg = Config()
    print("Base Path: ", cfg.getBasePath())
    print("Target Path: ", cfg.getTargetPath())
    print("Extension: ", cfg.getExtensions())
    print("Xml Name: ", cfg.getXmlName())
    print("Scrapper Xml Name: ", cfg.getScrapperXmlName())
    print("Retroarch Path: ", cfg.getRetroarchPath())
    print("Core Libary Name: ", cfg.getCoreLibaryName("gb"))
    cfg.save()