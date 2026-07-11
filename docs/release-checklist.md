# FlowForge Release Checklist

This document provides a standard operating procedure for maintainers to cut a new release of FlowForge.

## 1. Pre-Release Validation
- [ ] Run the complete test suite: `uv run pytest tests/`
- [ ] Ensure all documentation matches the target release version.
- [ ] Review `ROADMAP.md` and ensure current mission objectives are completed.
- [ ] Perform a full fresh-environment installation test using the CLI.

## 2. Version Bump
- [ ] Update `version` in `pyproject.toml`.
- [ ] Update `version` strings inside `src/flowforge/entrypoints/cli/main.py`.
- [ ] Update `version` in any relevant documentation/README examples.

## 3. Changelog Update
- [ ] Add the new release section to `CHANGELOG.md`.
- [ ] Summarize breaking changes, features, and bugfixes.
- [ ] Ensure date format is `YYYY-MM-DD`.

## 4. Build Package
- [ ] Run `uv build`.
- [ ] Verify that both `sdist` (`.tar.gz`) and `wheel` (`.whl`) are successfully generated in the `dist/` directory.

## 5. Git Tagging
- [ ] Commit all changes: `git commit -m "chore(release): vX.Y.Z"`
- [ ] Create an annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push changes and tags: `git push origin main --tags`

## 6. PyPI Publication
- [ ] Publish the package to PyPI: `uv publish` (Ensure you have configured your API token).
- [ ] Verify the package page on PyPI (authors, URLs, and formatting).

## 7. Post-Release
- [ ] Create a GitHub Release using the Git tag and copy the CHANGELOG.md contents into the release description.
- [ ] Update `ROADMAP.md` to point to the next phase/version.
