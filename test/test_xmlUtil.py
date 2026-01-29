# test_xmlUtil.py
# Tests for xmlUtil module

import pytest


class TestXmlUtil:
    """Tests for XmlManager class."""

    @pytest.fixture
    def rom_dir(self):
        """ROM directory for tests."""
        return 'anux'

    @pytest.fixture
    def setup_environment(self, rom_dir):
        """Setup test environment."""
        import config
        import fileUtil
        fileUtil.changeSubRomDir(rom_dir)
        rom_count = fileUtil.getRomCount()
        return {'rom_dir': rom_dir, 'rom_count': rom_count}

    @pytest.fixture
    def xml_manager(self, setup_environment):
        """Create XmlManager instance."""
        import xmlUtil
        return xmlUtil.XmlManager()

    def test_init(self, xml_manager, setup_environment):
        """Test XmlManager initialization."""
        assert xml_manager.size() > 0

    def test_xml_create(self, xml_manager, setup_environment):
        """Test XML creation."""
        rom_count = setup_environment['rom_count']

        # Force create new XML
        count = xml_manager.createXML(force=True)
        assert count == rom_count

        # Should skip if already exists
        count = xml_manager.createXML()
        assert count == 0

        # After createXML, manager state is cleared
        assert xml_manager.xmlRoot is None
        assert xml_manager.gameMap == {}
        assert xml_manager.size() == 0

    def test_load_xml(self, setup_environment):
        """Test loading XML file."""
        import xmlUtil
        rom_count = setup_environment['rom_count']

        manager = xmlUtil.XmlManager()
        manager.clear()
        assert manager.xmlRoot is None

        manager.readGamesFromXml()
        assert manager.xmlRoot is not None
        assert manager.gameMap is not None
        assert manager.size() == rom_count

    def test_find_game_by_idx(self, xml_manager):
        """Test finding game by index."""
        xml_manager.reload()

        game = xml_manager.findGameByIdx(0)
        assert game is not None
        assert 'name' in game
        assert 'path' in game

        # Out of bounds returns None
        invalid_game = xml_manager.findGameByIdx(len(xml_manager.gameList))
        assert invalid_game is None

    def test_find_game_by_path(self, xml_manager):
        """Test finding game by path."""
        xml_manager.reload()

        game = xml_manager.findGameByIdx(0)
        found_game = xml_manager.findGameByPath(game['path'])
        assert found_game == game

        # Invalid path returns None
        not_found = xml_manager.findGameByPath("invalid_path_xyz123")
        assert not_found is None

    def test_games_sorted(self, xml_manager, setup_environment):
        """Test that game list is sorted alphabetically."""
        xml_manager.reload()
        games = xml_manager.gameList
        rom_count = setup_environment['rom_count']

        assert len(games) == rom_count

        for i in range(1, len(games)):
            assert games[i]['name'] >= games[i-1]['name'], \
                f"Games not sorted: {games[i-1]['name']} should come before {games[i]['name']}"
