import sys
import pytest
from unittest.mock import patch
from io import StringIO
from flowforge.entrypoints.cli.main import main
from flowforge.utils.version import get_version, get_display_version

def test_get_version_matches_pyproject():
    version = get_version()
    assert version != "0.0.0-unknown"
    assert len(version.split(".")) >= 2

def test_cli_version_subcommand(capsys):
    testargs = ["flowforge", "version"]
    with patch.object(sys, "argv", testargs):
        main()
        
    captured = capsys.readouterr()
    assert "FlowForge CLI" in captured.out
    assert get_display_version() in captured.out

def test_cli_version_flag(capsys):
    testargs = ["flowforge", "--version"]
    with patch.object(sys, "argv", testargs):
        # argparse version action always raises SystemExit(0)
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        
    captured = capsys.readouterr()
    assert "FlowForge CLI" in captured.out
    assert get_display_version() in captured.out
