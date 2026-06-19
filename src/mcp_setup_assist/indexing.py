# Copyright (c) 2026 Christian Ekiza

"""Generic indexing utilities for codebase-memory-mcp."""
import shutil
import subprocess
import sys
from pathlib import Path


def run_index(venv_path: Path, packages: list[str], project_folders: list[Path], cbmignore_file: Path):
    """Index one or more packages from a venv and any project-specific folders.

    All paths must be absolute: venv_path, each entry in project_folders, and cbmignore_file.
    """
    # Index all directories that make up each package (handles editable/local installs)
    for package in packages:
        ns_paths = find_namespace_paths(venv_path, package)
        if ns_paths:
            for ns_path in ns_paths:
                apply_cbmignore(ns_path, cbmignore_file)
                index_path(ns_path)
        else:
            print(f"[WARN] {package} not found in venv — skipping")

    # Index project-specific folders
    for folder in project_folders:
        if folder.is_dir():
            index_path(folder)
        else:
            print(f"[INFO] {folder} not found — skipping")

    print("\n[DONE] Indexing complete.")


def find_namespace_paths(venv: Path, package: str) -> list[Path]:
    """Return all directories that make up a package, using the venv's Python.

    Works for regular installs, editable installs, and local folder installs.
    """
    python = venv / "Scripts" / "python.exe"
    if not python.exists():
        python = venv / "bin" / "python"

    result = subprocess.run(
        [str(python), "-c",
         f"import importlib.util; spec = importlib.util.find_spec('{package}'); "
         f"print('\\n'.join(spec.submodule_search_locations) if spec else '')"],
        capture_output=True, text=True
    )
    return [Path(p) for p in result.stdout.splitlines() if p.strip()]


def apply_cbmignore(target_path: Path, cbmignore_file: Path):
    """Copy a .cbmignore file into the target directory."""
    dst = target_path / ".cbmignore"
    shutil.copy2(cbmignore_file, dst)


def index_path(path: Path) -> bool:
    """Run codebase-memory-mcp index_repository on a path. Returns True on success."""
    abs_path = str(path.resolve()).replace("\\", "/")
    print(f"[INFO] Indexing: {abs_path}")
    result = subprocess.run(
        ["codebase-memory-mcp", "cli", "index_repository", f'{{"repo_path": "{abs_path}"}}'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"[OK] Indexed: {abs_path}")
        return True
    else:
        print(f"[ERROR] Failed to index: {abs_path}", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return False
