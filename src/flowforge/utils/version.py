import os
import re
import sys

def get_version() -> str:
    """
    Returns the authoritative version of the FlowForge package.
    Resolves version dynamically from package metadata, with a fallback
    to local pyproject.toml parsing for development workspaces.
    """
    # 1. Try reading from package metadata (when installed via pip/uv)
    try:
        if sys.version_info >= (3, 8):
            import importlib.metadata as importlib_metadata
        else:
            import importlib_metadata  # type: ignore
        return importlib_metadata.version("flowforge")
    except Exception:
        pass

    # 2. Fallback to parsing pyproject.toml in dev environments
    # We walk up from this file to find the root pyproject.toml
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Walk up to 5 levels
    for _ in range(5):
        pyproject_path = os.path.join(current_dir, "pyproject.toml")
        if os.path.exists(pyproject_path):
            try:
                with open(pyproject_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Look for version = "x.y.z" inside [project] block
                    # A robust regex for standard pyproject.toml
                    match = re.search(r'(?ms)^\[project\].*?^version\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
            except Exception:
                pass
        current_dir = os.path.dirname(current_dir)

    return "0.0.0-unknown"
