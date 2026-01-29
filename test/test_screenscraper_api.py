# test_screenscraper_api.py
# Tests for ScreenScraper API

import pytest
import requests


class TestScreenScraperAPI:
    """Tests for ScreenScraper API connection and functionality."""

    @pytest.fixture
    def api(self):
        """Create ScreenScraperAPI instance."""
        from screenScraper import ScreenScraperAPI
        return ScreenScraperAPI()

    def test_api_configured(self, api):
        """Test that API credentials are configured."""
        assert api.devid is not None
        assert api.devpassword is not None
        assert len(api.devid) > 0
        assert len(api.devpassword) > 0

    def test_api_connection(self, api):
        """Test API connection with known game hash."""
        # Test data: Ultima - Quest of the Avatar (U).zip
        system_id = 3  # NES
        test_md5 = "D370C3788F5FE2FA6E02E9DEADC7F56B"
        test_crc = "C7F5B3D8"

        params = {
            'devid': api.devid,
            'devpassword': api.devpassword,
            'softname': api.softname,
            'output': 'json',
            'systemeid': system_id,
            'md5': test_md5,
            'crc': test_crc
        }

        url = "https://www.screenscraper.fr/api2/jeuInfos.php"
        response = requests.get(url, params=params, timeout=30)

        # API should respond (200 = found, 404 = not found but connection works)
        assert response.status_code in [200, 404, 430]  # 430 = quota exceeded

    @pytest.mark.skip(reason="Requires actual ROM file")
    def test_search_game(self, api):
        """Test searching for a game."""
        # This test requires an actual ROM file
        pass

    def test_get_system_id(self):
        """Test system ID mapping."""
        from screenScraper import getSystemId

        # Test known systems
        assert getSystemId('nes') == 3
        assert getSystemId('snes') == 4
        assert getSystemId('megadrive') == 1
        assert getSystemId('gb') == 9
        assert getSystemId('gba') == 12

        # Unknown system returns None
        assert getSystemId('unknown_system_xyz') is None
