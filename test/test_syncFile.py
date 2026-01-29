# test_syncFile.py
# Tests for syncFile module

import pytest


@pytest.mark.requires_ssh
@pytest.mark.integration
class TestSyncFile:
    """Tests for SyncFile SSH functionality.

    These tests require SSH connection to groovy server.
    Run with: pytest -m requires_ssh
    """

    @pytest.fixture
    def sync_file(self):
        """Create and connect SyncFile instance."""
        from config import Config
        from syncFile import SyncFile
        import fileUtil

        sub_rom = "gb"
        fileUtil.changeSubRomDir(sub_rom)

        sync = SyncFile()
        sync.setServerInfo("groovy")
        connected = sync.connectSSH()

        if not connected:
            pytest.skip("Cannot connect to SSH server")

        yield sync

        sync.disconnectSSH()

    def test_connection(self, sync_file):
        """Test SSH connection is established."""
        assert sync_file.connected is True

    def test_copy_remote_list(self, sync_file):
        """Test copying remote list."""
        result = sync_file.copyRemoteList()
        assert result[0] is not None, "Expected local path"
        assert result[1] is not None, "Expected remote path"

    def test_export_local_list(self, sync_file):
        """Test exporting local list."""
        result = sync_file.exportLocalList()
        assert result[0] is not None, "Expected local path"
        assert result[1] is not None, "Expected remote path"
