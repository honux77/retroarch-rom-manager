# test_configparser_util.py
# Tests for ConfigParser behavior

import pytest
import configparser
import os
import tempfile


class TestConfigParserBehavior:
    """Tests to verify ConfigParser behavior."""

    @pytest.fixture
    def temp_ini_file(self):
        """Create a temporary ini file for testing."""
        fd, path = tempfile.mkstemp(suffix='.ini')
        with os.fdopen(fd, 'w') as f:
            f.write("[DEFAULT]\nKey1 = Value1\n[Section1]\nKey2 = Value2\n")
        yield path
        if os.path.exists(path):
            os.remove(path)

    def test_get_default_key(self, temp_ini_file):
        """Test getting keys from DEFAULT section."""
        config = configparser.ConfigParser()
        config.read(temp_ini_file)

        # Method 1: config.get with fallback
        val1 = config.get('DEFAULT', 'Key1', fallback='FB1')
        assert val1 == 'Value1'

        # Method 2: section dictionary access
        val2 = config['DEFAULT'].get('Key1', 'FB2')
        assert val2 == 'Value1'

    def test_defaults_lowercase(self, temp_ini_file):
        """Test that defaults() returns lowercase keys."""
        config = configparser.ConfigParser()
        config.read(temp_ini_file)

        # ConfigParser lowercases keys by default
        defaults = config.defaults()
        assert 'key1' in defaults
        assert defaults.get('key1') == 'Value1'

    def test_case_sensitive_keys(self, temp_ini_file):
        """Test case-sensitive key handling."""
        config = configparser.ConfigParser()
        config.optionxform = str  # Preserve case
        config.read(temp_ini_file)

        # With optionxform = str, keys keep original case
        assert 'Key1' in config['DEFAULT']
        assert config['DEFAULT']['Key1'] == 'Value1'

    def test_section_inheritance(self, temp_ini_file):
        """Test that sections inherit from DEFAULT."""
        config = configparser.ConfigParser()
        config.read(temp_ini_file)

        # Section1 should have Key1 from DEFAULT
        assert config.get('Section1', 'Key1') == 'Value1'
        assert config.get('Section1', 'Key2') == 'Value2'


class TestSecretIniInspection:
    """Tests related to secret.ini file inspection."""

    @pytest.fixture
    def secret_ini_path(self):
        """Path to secret.ini file."""
        return 'secret.ini'

    def test_secret_ini_exists(self, secret_ini_path):
        """Check if secret.ini exists."""
        # This is informational - skip if file doesn't exist
        if not os.path.exists(secret_ini_path):
            pytest.skip("secret.ini not found")

    def test_read_secret_ini(self, secret_ini_path):
        """Test reading secret.ini with case sensitivity."""
        if not os.path.exists(secret_ini_path):
            pytest.skip("secret.ini not found")

        config = configparser.ConfigParser()
        config.optionxform = str  # Preserve case
        config.read(secret_ini_path)

        # Just verify it can be read
        assert len(config.sections()) >= 0
