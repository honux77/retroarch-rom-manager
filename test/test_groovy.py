# test_groovy.py
# Tests for groovy module

import pytest


class TestGroovy:
    """Tests for Groovy export functionality."""

    @pytest.fixture
    def setup_mame(self):
        """Setup MAME directory for groovy tests."""
        import config
        import fileUtil
        from xmlUtil import XmlManager

        sub_dir = 'mame'
        fileUtil.changeSubRomDir(sub_dir)
        return {
            'config': config.Config(),
            'xml_manager': XmlManager(),
            'sub_dir': sub_dir
        }

    def test_read_csv(self, setup_mame):
        """Test reading Groovy CSV file."""
        import groovy
        groovy_data = groovy.readCsv()
        assert len(groovy_data) > 0, "Expected CSV data"

    def test_export_groovy_list(self, setup_mame):
        """Test exporting Groovy list from XML."""
        import groovy
        match, total = groovy.exportGroovyList(dryRun=False)

        assert total > 0, "Expected some games"
        assert match > 0, "Expected some matches"
        assert match == total, f"Expected all games to match: {match}/{total}"
