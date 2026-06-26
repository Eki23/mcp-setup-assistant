# mcp-setup-assist

Generic utilities for configuring [codebase-memory-mcp](https://pypi.org/project/codebase-memory-mcp) in any Python project. Designed as a foundation for project-specific setup tools — handle the mechanics here, keep only project-specific defaults in the consumer package.

## What It Does

- Resolves installed packages to their source directories via `pip show` (supports regular, editable, and system-wide installs)
- Indexes one or more source trees into a `codebase-memory-mcp` knowledge graph — either as a single combined project (default) or as separate independent projects
- Registers the `codebase-memory-mcp` MCP server with your IDE (Amazon Q, Claude, Cursor)
- Copies agent rules and `.cbmignore` files into the correct IDE config locations
- Provides a generic CLI builder so consumers expose a consistent `init` / `index` interface

## Installation

```bash
pip install mcp-setup-assist
```

## Building on top of this package

`mcp-setup-assist` is a library, not an end-user tool. The typical pattern is to create a thin project-specific package that defines defaults and delegates to the generic functions:

```python
# myproject_mcp/index.py
from mcp_setup_assist.indexing import run_index as _run_index
from myproject_mcp.templates import get_template_path

PACKAGES = ["my-lib", "my-other-lib"]
PROJECT_FOLDERS = ["src", "custom"]
STAGING_DIR = ".myproject-index"

def run_index(venv_path, extra_packages=None, extra_folders=None,
              include_system_packages=True, separate_packages=False):
    _run_index(
        venv_path=venv_path,
        packages=PACKAGES + (extra_packages or []),
        project_folders=PROJECT_FOLDERS + (extra_folders or []),
        cbmignore_file=get_template_path(".cbmignore"),
        include_system_packages=include_system_packages,
        separate_packages=separate_packages,
        staging_dir_name=STAGING_DIR,
    )
```

```python
# myproject_mcp/cli.py
from mcp_setup_assist.cli import run_cli
from myproject_mcp.init import run_init
from myproject_mcp.index import run_index

def main():
    run_cli("myproject-mcp", "Configure codebase-memory-mcp for My Project",
            init_fn=run_init, index_fn=run_index)
```

## Modules

### `mcp_setup_assist.indexing`

| Symbol | Description |
|--------|-------------|
| `run_index(venv_path, packages, project_folders, cbmignore_file, *, include_system_packages=True, separate_packages=False, staging_dir_name=".cbm-index")` | Resolve packages, deduplicate, and index — combined by default |
| `index_combined(named_folders, project_root, cbmignore_file, staging_dir_name=".cbm-index")` | Stage multiple source trees via directory junctions/symlinks and index as one project |
| `ensure_gitignore(project_root, entry)` | Append an entry to `.gitignore`, creating it if needed |
| `apply_cbmignore(target_path, cbmignore_file)` | Copy a `.cbmignore` into a directory |
| `index_path(path)` | Run `codebase-memory-mcp index_repository` on a path; returns `True` on success |
| `STAGING_DIR` | Default staging directory name: `".cbm-index"` |

**Package resolution** uses `pip show` — the venv Python is tried first, system Python second (when `include_system_packages=True`). Editable installs return their source tree; regular installs return the correct subdirectory inside site-packages via `top_level.txt`.

**Combined indexing** creates a staging directory containing directory junctions (Windows) or symlinks (Unix) for each source tree, then indexes that single directory. This makes the full inheritance chain visible as one graph. The staging directory is added to `.gitignore` automatically.

### `mcp_setup_assist.agents`

| Symbol | Description |
|--------|-------------|
| `run_init(agents, rules_file, cbmignore_file)` | Register the MCP server and copy rules for each agent |
| `write_mcp_config(project_root, agent)` | Write (or merge) `mcp.json` / `settings.json` |
| `write_rules(project_root, agent, rules_file)` | Copy rules file to the agent's rules directory |
| `write_cbmignore(project_root, cbmignore_file)` | Copy `.cbmignore` to the project root |
| `AGENT_CONFIGS` | Config paths for `amazonq`, `claude`, `cursor` |
| `MCP_SERVER_CONFIG` | The `codebase-memory-mcp` server JSON block |

### `mcp_setup_assist.cli`

| Symbol | Description |
|--------|-------------|
| `run_cli(prog, description, init_fn, index_fn)` | Build and run the standard `init` / `index` CLI |

The `index` subcommand exposes:

| Flag | Default | Description |
|------|---------|-------------|
| `--venv PATH` | `.venv` | Path to the virtual environment |
| `--package NAME` | — | Extra package(s) to index (comma-separated or repeatable) |
| `--folder PATH` | — | Extra folder(s) to index (comma-separated or repeatable) |
| `--include-system-packages` / `--no-…` | enabled | Fall back to system Python for packages not found in the venv |
| `--index-as-separate-packages` | disabled | Index each source tree independently instead of combining |

## License

Apache 2.0 — see [LICENSE](LICENSE).
