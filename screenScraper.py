# screenScraper.py
# ScreenScraper API V2 클라이언트

import requests
import hashlib
import zipfile
import os
from config import Config

# ScreenScraper 시스템 ID 매핑
SYSTEM_IDS = {
    'nes': 3,
    'fds': 106,
    'snes': 4,
    'gb': 9,
    'gbc': 10,
    'gba': 12,
    'megadrive': 1,
    'mastersystem': 2,
    'pcengine': 31,
    'pcenginecd': 114,
    'saturn': 22,
    'mame': 75,
    'fbneo': 75,
    'msx1': 113,
    'msx2': 116,
    'x68000': 79,
    'pc98': 208,
    'n64': 14,
    'wswan': 45,
}

API_BASE_URL = "https://api.screenscraper.fr/api2"


class ScreenScraperAPI:
    def __init__(self):
        self.config = Config()
        self.devid = "xxx"
        self.devpassword = "yyy"
        self.softname = "zzz"
        self.ssid = "test"
        self.sspassword = "test"
        self._loadCredentials()

    def _loadCredentials(self):
        """secret.ini에서 ScreenScraper 계정 및 개발자 정보를 로드"""
        try:
            # 개발자 정보 로드
            devid = self.config.getScreenScraperDevID()
            if devid: self.devid = devid
            
            devpassword = self.config.getScreenScraperDevPassword()
            if devpassword: self.devpassword = devpassword

            # 사용자 정보 로드
            ssid = self.config.getScreenScraperID()
            if ssid: self.ssid = ssid

            sspassword = self.config.getScreenScraperPassword()
            if sspassword: self.sspassword = sspassword

        except Exception as e:
            print(f"ScreenScraper 계정 정보 로드 실패: {e}")
        return True

    def isConfigured(self):
        """계정 정보가 설정되어 있는지 확인"""
        # xxx, test 등 플레이스홀더도 api. 서브도메인에서 동작하므로 
        # 비어있지만 않으면 설정된 것으로 간주합니다.
        return all([self.devid, self.devpassword, self.ssid, self.sspassword])

    def _calculateHashes(self, filePath):
        """파일의 CRC32, MD5, SHA1 해시 계산"""
        # zip 파일인 경우 내부 파일의 해시 계산
        if filePath.lower().endswith('.zip'):
            try:
                with zipfile.ZipFile(filePath, 'r') as zf:
                    # 첫 번째 파일의 해시 계산
                    for name in zf.namelist():
                        if not name.endswith('/'):
                            with zf.open(name) as f:
                                data = f.read()
                                return self._hashData(data)
            except Exception as e:
                print(f"ZIP 파일 해시 계산 실패: {e}")
                return None, None, None

        # 일반 파일
        try:
            with open(filePath, 'rb') as f:
                data = f.read()
                return self._hashData(data)
        except Exception as e:
            print(f"파일 해시 계산 실패: {e}")
            return None, None, None

    def _hashData(self, data):
        """바이트 데이터의 해시 계산"""
        import binascii
        crc32 = format(binascii.crc32(data) & 0xFFFFFFFF, '08X')
        md5 = hashlib.md5(data).hexdigest().upper()
        sha1 = hashlib.sha1(data).hexdigest().upper()
        return crc32, md5, sha1

    def searchGame(self, romPath, systemId, romName=None):
        """
        게임 정보 검색

        Args:
            romPath: ROM 파일 경로
            systemId: ScreenScraper 시스템 ID
            romName: ROM 파일명 (옵션)

        Returns:
            게임 정보 딕셔너리 또는 None
        """
        if not self.isConfigured():
            print("ScreenScraper 계정이 설정되지 않았습니다.")
            return None

        # 해시 계산
        crc32, md5, sha1 = None, None, None
        if os.path.exists(romPath):
            crc32, md5, sha1 = self._calculateHashes(romPath)
            print(f"해시 계산 완료 - CRC32: {crc32}, MD5: {md5}")

        # API 파라미터 구성
        params = {
            'devid': self.devid,
            'devpassword': self.devpassword,
            'softname': self.softname,
            'ssid': self.ssid,
            'sspassword': self.sspassword,
            'output': 'json',
            'systemeid': systemId,
        }

        # 해시 또는 파일명으로 검색
        if crc32:
            params['crc'] = crc32
        if md5:
            params['md5'] = md5
        if sha1:
            params['sha1'] = sha1
        if romName:
            params['romnom'] = romName

        try:
            url = f"{API_BASE_URL}/jeuInfos.php"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, params=params, headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json()
                if 'response' in data and 'jeu' in data['response']:
                    return data['response']['jeu']
                else:
                    print(f"게임을 찾을 수 없습니다: {data}")
                    return None
            else:
                print(f"API 오류: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            print("API 요청 타임아웃")
            return None
        except Exception as e:
            print(f"API 요청 실패: {e}")
            return None

    def getGameImages(self, gameData, imageTypes=None):
        """
        게임 데이터에서 이미지 URL 추출

        Args:
            gameData: searchGame에서 반환된 게임 데이터
            imageTypes: 원하는 이미지 타입 리스트 (예: ['ss', 'box-2D', 'wheel'])

        Returns:
            이미지 타입별 URL 딕셔너리
        """
        if not gameData or 'medias' not in gameData:
            return {}

        if imageTypes is None:
            imageTypes = ['ss', 'box-2D', 'box-3D', 'wheel', 'screenmarquee']

        images = {}
        medias = gameData.get('medias', [])

        for media in medias:
            mediaType = media.get('type', '')
            if mediaType in imageTypes:
                # 지역 우선순위: kr > jp > wor > us > eu
                url = media.get('url', '')
                region = media.get('region', 'wor')

                if mediaType not in images:
                    images[mediaType] = {'url': url, 'region': region}
                elif region in ['kr', 'jp'] and images[mediaType]['region'] not in ['kr', 'jp']:
                    images[mediaType] = {'url': url, 'region': region}

        return {k: v['url'] for k, v in images.items()}

    def downloadImage(self, imageUrl, savePath):
        """
        이미지 다운로드

        Args:
            imageUrl: 이미지 URL
            savePath: 저장 경로

        Returns:
            성공 여부
        """
        try:
            # API 인증 정보 추가
            params = {
                'devid': self.devid,
                'devpassword': self.devpassword,
                'softname': self.softname,
                'ssid': self.ssid,
                'sspassword': self.sspassword,
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(imageUrl, params=params, headers=headers, timeout=60)

            if response.status_code == 200:
                # 디렉토리 생성
                os.makedirs(os.path.dirname(savePath), exist_ok=True)

                with open(savePath, 'wb') as f:
                    f.write(response.content)
                print(f"이미지 저장 완료: {savePath}")
                return True
            else:
                print(f"이미지 다운로드 실패: {response.status_code}")
                return False

        except Exception as e:
            print(f"이미지 다운로드 오류: {e}")
            return False

    def getGameInfo(self, gameData, lang='ko'):
        """
        게임 정보 추출 (이름, 설명 등)

        Args:
            gameData: searchGame에서 반환된 게임 데이터
            lang: 언어 코드 (ko, en, jp 등)

        Returns:
            게임 정보 딕셔너리
        """
        if not gameData:
            return {}

        info = {
            'id': gameData.get('id', ''),
            'name': '',
            'description': '',
            'developer': '',
            'publisher': '',
            'releasedate': '',
            'genre': '',
            'players': '',
            'rating': '',
        }

        # 이름 추출 (언어 우선순위)
        names = gameData.get('noms', [])
        for name in names:
            region = name.get('region', '')
            if region == lang or (info['name'] == '' and region in ['wor', 'us', 'eu', 'jp']):
                info['name'] = name.get('text', '')
                if region == lang:
                    break

        # 설명 추출
        synopsis = gameData.get('synopsis', [])
        for syn in synopsis:
            synLang = syn.get('langue', '')
            if synLang == lang or (info['description'] == '' and synLang in ['en', 'jp']):
                info['description'] = syn.get('text', '')
                if synLang == lang:
                    break

        # 기타 정보
        info['developer'] = gameData.get('developpeur', {}).get('text', '')
        info['publisher'] = gameData.get('editeur', {}).get('text', '')

        dates = gameData.get('dates', [])
        if dates:
            info['releasedate'] = dates[0].get('text', '')

        genres = gameData.get('genres', [])
        if genres:
            genreNames = [g.get('noms', [{}])[0].get('text', '') for g in genres if g.get('noms')]
            info['genre'] = ', '.join(genreNames)

        info['players'] = gameData.get('joueurs', {}).get('text', '')
        info['rating'] = gameData.get('note', {}).get('text', '')

        return info


def getSystemId(subRomDir):
    """서브 롬 디렉토리명으로 ScreenScraper 시스템 ID 반환"""
    return SYSTEM_IDS.get(subRomDir.lower(), None)


# 테스트 코드
if __name__ == "__main__":
    api = ScreenScraperAPI()
    print(f"계정 설정됨: {api.isConfigured()}")
