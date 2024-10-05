import json
import os
from os import path

class LastStatus:
    '''
    프로그램의 마지막 상태를 저장하는 클래스
    마지막 상태는 lastStatus.json 파일에 저장된다.
    '''
    
    def __init__(self):                
        self.jsonFileName = path.join(os.getcwd(), 'lastStatus.json')
        self.load()


    def load(self):
        '''
        마지막 상태 파일을 읽어서 객체에 저장한다.
        마지막 상태 파일이 없으면 새로운 파일을 생성한다.
        '''
        if path.exists(self.jsonFileName):
            self.lastStatusJson = json.load(open(self.jsonFileName, 'r+'))
        else:
            print("미자믹 상태 저장 파일이 없어 새로 생성합니다.")
            self.lastStatusJson = self.__createDefaultFile()

    def save(self):
        '''
        마지막 상태 파일을 저장한다.
        '''
        json.dump(self.lastStatusJson, open(self.jsonFileName, 'w+'), indent=4)

    def getLastSubRomDirectory(self):
        '''
        마지막으로 선택한 롬폴더를 반환한다.
        '''
        return self.lastStatusJson['lastSubRomDirectory']

    def setLastSubRomDirectory(self, lastSubRomDirectory):
        '''
        마지막으로 선택한 롬폴더를 경로를 설정한다.
        '''
        self.lastStatusJson['lastSubRomDirectory'] = lastSubRomDirectory
    
    def getLastRomName(self):
        '''
        마지막으로 선택한 롬의 인덱스를 반환한다.
        '''
        return self.lastStatusJson['lastRomName']
    
    def setLastRomName(self, lastRomName):
        '''
        마지막으로 선택한 롬의 인덱스를 설정한다.
        '''
        self.lastStatusJson['lastRomName'] = lastRomName
        
    def __createDefaultFile(self):
        '''
        마지막 상태 파일이 없을 때 기본 마지막 상태 파일을 생성한다.
        '''
        defaultJson =   {
            "lastSubRomDirectory": "unknown",
            "lastRomName": "unknown"            
        }

        json.dump(defaultJson, open(self.jsonFileName, 'w+'), indent=4)
        return defaultJson
    
    
# main function for test
if __name__ == "__main__":
    lastStatus = LastStatus()
    print("Sub Rom Dir:", lastStatus.getLastSubRomDirectory())
    print("Rom Index:", lastStatus.getLastRomIndex())
