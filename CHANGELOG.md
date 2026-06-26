# Changelog

All notable changes to this project will be documented in this file.

## [0.7.0] - 2026-06-26

### Added

- `index_combined(named_folders, project_root, cbmignore_file, staging_dir_name)` — public function that stages multiple source trees as directory junctions (Windows) or symlinks (Unix) under a single staging directory and indexes them as one `codebase-memory-mcp` project, making cross-package inheritance chains visible in one graph
- `ensure_gitignore(project_root, entry)` — appends an entry to `.gitignore`, creating the file if it does not exist; called automatically when a staging directory is created
- `STAGING_DIR = ".cbm-index"` — module-level default staging directory name; consumers can override by passing `staging_dir_name` to `run_index` or `index_combined`
- `run_index` gains two new keyword-only parameters: `include_system_packages` (default `True`) and `separate_packages` (default `False`); `staging_dir_name` (default `STAGING_DIR`) is also accepted and forwarded to `index_combined`
- `run_cli` index subcommand gains `--include-system-packages` / `--no-include-system-packages` (`BooleanOptionalAction`, default enabled) and `--index-as-separate-packages` (`store_true`); both are forwarded to `index_fn`

### Changed

- Package resolution replaced: `find_namespace_paths` (which used `importlib.util.find_spec`) is superseded by a `pip show`-based pipeline — `_pip_show` prefers `Editable project location` over `Location` so editable installs correctly return their source tree; `_top_level_names` reads `top_level.txt` from dist-info via `importlib.metadata` to find the real installed directory name (handles packages that install into a shared namespace)
- System Python fallback added to package resolution: `_find_system_python` locates the Python executable at `sys.base_prefix`; when `include_system_packages=True`, packages not found in the venv are retried against system Python
- Combined indexing is now the default in `run_index`; separate-package mode is opt-in via `separate_packages=True` or `--index-as-separate-packages`
- Deduplication in `run_index` now runs across both project folders and resolved package paths, preserving first-seen label; paths that do not resolve to an existing directory are silently dropped
- `hello.py` (`Greeter`) removed — scaffolding placeholder, no longer part of the public API


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
