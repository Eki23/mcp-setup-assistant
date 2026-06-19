# Copyright (c) 2026 Christian Ekiza

"""Generic indexing utilities for codebase-memory-mcp."""
import shutil
import subprocess
import sys
from pathlib import Path


def run_index(venv_path: Path, namespace: str, project_folders: list[Path], cbmignore_file: Path):
    """Index a namespace from site-packages and any project-specific folders.

    All paths must be absolute: venv_path, each entry in project_folders, and cbmignore_file.
    """
    # Index site-packages namespace
    ns_path = find_namespace_in_venv(venv_path, namespace)
    if ns_path:
        apply_cbmignore(ns_path, cbmignore_file)
        index_path(ns_path)
    else:
        print(f"[WARN] {namespace} not found in {venv_path}/site-packages — skipping base library indexing")

    # Index project-specific folders
    for folder in project_folders:
        if folder.is_dir():
            index_path(folder)
            

    print("\n[DONE] Indexing complete.")


def find_namespace_in_venv(venv: Path, namespace: str) -> Path | None:
    """Find a namespace package directory in a venv's site-packages."""
    # Windows
    candidate = venv / "Lib" / "site-packages" / namespace
    if candidate.is_dir():
        return candidate
    # Linux/macOS
    for p in (venv / "lib").glob(f"python*/site-packages/{namespace}"):
        if p.is_dir():
            return p
    return None


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
