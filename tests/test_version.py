import pytest
from flowforge.utils.version import get_display_version, format_display_version

def test_format_display_version():
    # Standard releases
    assert format_display_version("1.0.0") == "1.0.0"
    assert format_display_version("2.1.3") == "2.1.3"

    # Alphas
    assert format_display_version("1.0.0a0") == "1.0.0-alpha"
    assert format_display_version("1.0.0a1") == "1.0.0-alpha.1"
    assert format_display_version("2.5.1a2") == "2.5.1-alpha.2"

    # Betas
    assert format_display_version("1.0.0b0") == "1.0.0-beta"
    assert format_display_version("1.0.0b1") == "1.0.0-beta.1"
    assert format_display_version("1.0.0b2") == "1.0.0-beta.2"

    # Release Candidates
    assert format_display_version("1.0.0rc0") == "1.0.0-rc"
    assert format_display_version("1.0.0rc1") == "1.0.0-rc.1"
    assert format_display_version("3.0.0rc3") == "3.0.0-rc.3"

    # Edge cases or unsupported formats gracefully fallback
    assert format_display_version("1.0.0-beta") == "1.0.0-beta"
    assert format_display_version("1.0.0.dev1") == "1.0.0.dev1"
    assert format_display_version("0.0.0-unknown") == "0.0.0-unknown"
