# test_fileUtil.py
# Tests for fileUtil module

import pytest
import os


class TestFileUtil:
    """Tests for fileUtil module."""

    @pytest.fixture
    def config(self):
        """Provide Config instance."""
        import config
        return config.Config()

    @pytest.fixture
    def sub_dir(self):
        """Default sub directory for tests."""
        return 'anux'

    def test_change_root_dir(self, config):
        """Test changing to root ROM directory."""
        import fileUtil
        fileUtil.changeRootDir()
        assert os.getcwd() == config.getBasePath()

    def test_change_sub_dir(self, config, sub_dir):
        """Test changing to sub ROM directory."""
        import fileUtil
        fileUtil.changeSubRomDir(sub_dir)
        expected_path = os.path.join(config.getBasePath(), sub_dir)
        assert os.getcwd() == expected_path

    def test_get_current_rom_dir_name(self, sub_dir):
        """Test getting current ROM directory name."""
        import fileUtil
        fileUtil.changeSubRomDir(sub_dir)
        current_dir = fileUtil.getCurrentRomDirName()
        assert current_dir == sub_dir

    def test_get_rom_count(self, sub_dir):
        """Test counting ROM files in directory."""
        import fileUtil
        fileUtil.changeSubRomDir(sub_dir)
        count = fileUtil.getRomCount()
        assert count > 0, f"Expected ROM files in {sub_dir}"

    def test_read_sub_dirs(self, config):
        """Test reading sub directories."""
        import fileUtil
        fileUtil.changeRootDir()
        sub_dirs = fileUtil.readSubDirs()
        assert len(sub_dirs) > 0, "Expected at least one sub directory"
        assert all(isinstance(d, str) for d in sub_dirs)
