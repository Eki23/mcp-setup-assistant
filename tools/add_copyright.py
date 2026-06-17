from pathlib import Path

COPYRIGHT_LINE = "# Copyright (c) 2026 Christian Ekiza\n"

EXTENSIONS = {".py", ".md", ".txt", ".toml", ".yaml", ".yml"}

COPYRIGHT_MARKERS = [
    "copyright",
    "Copyright",
]

CHECK_LINES = 10


def has_copyright(content: str) -> bool:
    # only inspect first N lines
    lines = content.splitlines()[:CHECK_LINES]
    return any(any(marker in line for marker in COPYRIGHT_MARKERS) for line in lines)


def add_copyright(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")

        if has_copyright(content):
            return  # skip if already present in top 10 lines

        new_content = COPYRIGHT_LINE + "\n" + content
        file_path.write_text(new_content, encoding="utf-8")

        print(f"Added copyright: {file_path}")

    except Exception as e:
        print(f"Skipping {file_path}: {e}")


def main():
    root = Path(".").resolve().parent / "src"

    for file_path in root.rglob("*"):
        print(f"Processing {file_path}")
        if file_path.is_file() and file_path.suffix in EXTENSIONS:
            add_copyright(file_path)


if __name__ == "__main__":
    main()