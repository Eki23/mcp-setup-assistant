# Copyright (c) 2026 Christian Ekiza

"""Generic indexing utilities for codebase-memory-mcp."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

STAGING_DIR = ".cbm-index"


def run_index(
    venv_path: "Path | str",
    packages: list,
    project_folders: list,
    cbmignore_file: Path,
    include_system_packages: bool = True,
    separate_packages: bool = False,
    staging_dir_name: str = STAGING_DIR,
):
    """Index packages and project folders into codebase-memory-mcp.

    Searches the venv first for each package, then system Python when
    include_system_packages is True. By default all sources are staged in a
    single directory and indexed as one project so cross-package call chains
    are visible in one graph.
    """
    project_root = Path.cwd()
    venv = Path(venv_path).resolve()
    venv_python = _venv_python(venv)
    sys_python = _find_system_python() if include_system_packages else None

    named = []  # list of (label, Path)

    for f in project_folders:
        p = Path(f)
        folder = p if p.is_absolute() else project_root / p
        named.append((p.name, folder))

    for package in packages:
        path = _find_package_path(venv_python, package, sys_python)
        if path:
            print(f'[INFO] "{package}" found at {path}')
            apply_cbmignore(path, cbmignore_file)
            named.append((package, path))
        else:
            print(f'[WARN] "{package}" not found — skipping')

    seen: set = set()
    unique = []
    for name, p in named:
        resolved = p.resolve()
        if resolved not in seen and resolved.is_dir():
            seen.add(resolved)
            unique.append((name, p))

    if separate_packages:
        for _, p in unique:
            apply_cbmignore(p, cbmignore_file)
            index_path(p)
        print("\n[DONE] Indexing complete.")
    else:
        index_combined(unique, project_root, cbmignore_file, staging_dir_name)


def index_combined(
    named_folders: list,
    project_root: Path,
    cbmignore_file: Path,
    staging_dir_name: str = STAGING_DIR,
):
    """Index all source trees as one project via a junction/symlink staging dir."""
    staging = project_root / staging_dir_name
    staging.mkdir(exist_ok=True)
    ensure_gitignore(project_root, f"{staging_dir_name}/")

    used: set = set()
    for name, source in named_folders:
        jname = _unique_name(name, used)
        used.add(jname)
        link = staging / jname
        _remove_link(link)
        if _create_junction(link, source.resolve()):
            print(f'[INFO] Staging "{jname}" → {source}')
        else:
            print(f'[WARN] Could not create junction for {source} — skipping')

    apply_cbmignore(staging, cbmignore_file)
    print(f'\n[INFO] Indexing combined project at {staging}')
    if index_path(staging):
        print('\n[DONE] Indexing complete.')
    else:
        print('\n[ERROR] Combined indexing failed.', file=sys.stderr)


def ensure_gitignore(project_root: Path, entry: str):
    """Append entry to .gitignore if not already listed, creating the file if needed."""
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if entry not in content:
            gitignore.write_text(
                content.rstrip("\n") + f"\n{entry}\n",
                encoding="utf-8",
            )
    else:
        gitignore.write_text(f"{entry}\n", encoding="utf-8")


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
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"[OK] Indexed: {abs_path}")
        return True
    else:
        print(f"[ERROR] Failed to index: {abs_path}", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return False


def _venv_python(venv: Path):
    for exe in (venv / "Scripts" / "python.exe", venv / "bin" / "python"):
        if exe.exists():
            return exe
    return None


def _find_system_python():
    base = Path(sys.base_prefix)
    for exe in (base / "python.exe", base / "python", base / "bin" / "python"):
        if exe.exists():
            return exe
    return None


def _find_package_path(venv_python, package: str, sys_python=None):
    if venv_python:
        path = _pip_show(venv_python, package)
        if path:
            return path
    if sys_python:
        return _pip_show(sys_python, package)
    return None


def _pip_show(python: Path, package: str):
    """Resolve a package to its source directory via pip show.

    Prefers 'Editable project location' over 'Location' so editable installs
    point at their actual source tree rather than site-packages.
    """
    result = subprocess.run(
        [str(python), "-m", "pip", "show", package],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    editable_location = None
    location = None
    for line in result.stdout.splitlines():
        if line.startswith("Editable project location:"):
            editable_location = Path(line.split(":", 1)[1].strip())
        elif line.startswith("Location:"):
            location = Path(line.split(":", 1)[1].strip())
    if editable_location and editable_location.is_dir():
        return editable_location
    if location:
        for name in _top_level_names(python, package):
            pkg_dir = location / name
            if pkg_dir.is_dir():
                return pkg_dir
    return None


def _top_level_names(python: Path, package: str) -> list:
    """Return top-level directory names from the package's dist-info."""
    result = subprocess.run(
        [
            str(python), "-c",
            f"import importlib.metadata as m; "
            f"d = m.Distribution.from_name({package!r}); "
            f"t = (d.read_text('top_level.txt') or '').strip(); "
            f"print(t)",
        ],
        capture_output=True, text=True,
    )
    names = [n.strip() for n in result.stdout.splitlines() if n.strip()]
    if not names:
        names = [package.replace("-", "_"), package]
    return names


def _unique_name(name: str, used: set) -> str:
    if name not in used:
        return name
    i = 2
    while f"{name}_{i}" in used:
        i += 1
    return f"{name}_{i}"


def _create_junction(link: Path, target: Path) -> bool:
    """Create a directory junction (Windows) or symlink (Unix)."""
    if sys.platform == "win32":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True, text=True,
        )
        return result.returncode == 0
    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except OSError:
        return False


def _remove_link(link: Path):
    """Remove a junction or symlink without deleting the target."""
    if sys.platform == "win32":
        subprocess.run(["cmd", "/c", "rmdir", str(link)], capture_output=True)
    else:
        try:
            link.unlink()
        except FileNotFoundError:
            pass
