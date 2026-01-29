# conftest.py
# Pytest configuration and shared fixtures

import pytest
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app_config():
    """Provide Config instance."""
    import config
    return config.Config()


@pytest.fixture
def change_to_base_dir(app_config):
    """Change to base ROM directory."""
    import fileUtil
    fileUtil.changeRootDir()
    yield
    # No cleanup needed - tests may change directories


@pytest.fixture
def sub_rom_dir():
    """Default sub ROM directory for tests."""
    return 'anux'


@pytest.fixture
def setup_sub_rom(sub_rom_dir):
    """Setup sub ROM directory."""
    import fileUtil
    fileUtil.changeSubRomDir(sub_rom_dir)
    return sub_rom_dir


@pytest.fixture
def xml_manager(setup_sub_rom):
    """Provide XmlManager instance."""
    from xmlUtil import XmlManager
    return XmlManager()
