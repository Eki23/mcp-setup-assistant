# Changelog

All notable changes to this project will be documented in this file.

## [0.6.1] - 2026-06-19

### Changed

- `run_index` now accepts `packages: list[str]` instead of a single `namespace: str`, allowing multiple top-level packages to be indexed in one pass
- All paths passed to `run_index` must now be absolute; callers are responsible for resolving relative paths
- Replaced `find_namespace_in_venv` with `find_namespace_paths`, which uses the venv's own Python (`importlib.util.find_spec`) to locate packages — correctly handles editable installs and local folder installs where code is not copied into site-packages
- `run_cli` now passes `--package` and `--folder` CLI arguments through to `index_fn`, enabling callers to extend defaults at runtime; both flags accept comma-separated values or can be repeated
- Missing project folders now emit `[INFO]` instead of silently skipping

## [0.6.0] - 2026-06-19

### Changed

- `run_index` now accepts `packages: list[str]` instead of a single `namespace: str`, allowing multiple top-level packages to be indexed in one pass
- All paths passed to `run_index` must now be absolute; callers are responsible for resolving relative paths
- Replaced `find_namespace_in_venv` with `find_namespace_paths`, which uses the venv's own Python (`importlib.util.find_spec`) to locate packages — correctly handles editable installs and local folder installs where code is not copied into site-packages
- Missing project folders now emit `[INFO]` instead of silently skipping

## [0.5.0] - 2026-06-18

- Added support for Claude agents
 
## [0.1.1] - 2026-06-16

- Bump version to 0.1.1.
- Add `requests` dependency to `pyproject.toml`.
- Update README with installation instructions.
- Minor documentation fixes.

## [0.1.0] - 2026-06-15

- Initial release.
- Basic project scaffolding and configuration.
