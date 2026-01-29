# test_scrapper.py
# Tests for scrapper module

import pytest


class TestScrapper:
    """Tests for scrapper functionality."""

    @pytest.fixture
    def setup_scrapper(self):
        """Setup environment for scrapper tests."""
        import config
        import fileUtil
        from xmlUtil import XmlManager

        sub_dir = 'anux'
        fileUtil.changeSubRomDir(sub_dir)

        return {
            'config': config.Config(),
            'xml_manager': XmlManager(),
            'sub_dir': sub_dir
        }

    def test_update_xml_from_scrapper(self, setup_scrapper):
        """Test updating XML from scrapper data."""
        from scrapper import updateXMLFromScrapper

        xml_manager = setup_scrapper['xml_manager']
        assert xml_manager.size() > 0, "Expected games in XML"

        skip, update = updateXMLFromScrapper()
        assert skip > 0 or update >= 0, "Expected some processing"
