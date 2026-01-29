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

    def test_api_connection(self, api):
        """Test API connection with known game."""
        # Test data: Sonic The Hedgehog 2 (World).zip
        system_id = 1  # Genesis/Megadrive
        test_crc = "50ABC90A"
        
        # We use searchGame directly to test the integration
        game_data = api.searchGame(
            romPath="Sonic The Hedgehog 2 (World).zip", # Path doesn't exist but we pass CRC
            systemId=system_id,
            romName="Sonic The Hedgehog 2 (World).zip"
        )
        
        # If API is working, it should return game data or at least not fail with 403
        # Since we are using 'test' credentials, let's see what happens
        assert game_data is not None
        assert game_data.get('id') == '3'

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
