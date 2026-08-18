"""
check_config.py

Checks config files in delivery/ for unreplaced placeholder values.
A placeholder is any value matching YOUR_<SOMETHING> in uppercase.

Scans:
  config.py   - Python config files
  config.yml  - YAML config files
  config.yaml - YAML config files
  config.ipynb - Notebook config files (code cells only)

Used as a pre-commit hook and in CI.
"""

import json
import re
import sys
from pathlib import Path

DELIVERY_DIR = Path("delivery")

# Matches YOUR_SOMETHING - uppercase letters, digits, and underscores after YOUR_
PLACEHOLDER_PATTERN = re.compile(r"\bYOUR_[A-Z0-9_]+\b")

# Config filenames to scan
CONFIG_FILENAMES = {"config.py", "config.yml", "config.yaml", "config.ipynb"}


def find_config_files(root: Path) -> list[Path]:
    return [
        p for p in root.rglob("*") if p.is_file() and p.name.lower() in CONFIG_FILENAMES
    ]


def check_text_file(filepath: Path) -> list[str]:
    errors = []
    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, start=1):
            for match in PLACEHOLDER_PATTERN.finditer(line):
                errors.append(
                    f"{filepath}:{line_num} - unreplaced placeholder "
                    f"'{match.group()}' found"
                )
    return errors


def check_notebook_file(filepath: Path) -> list[str]:
    errors = []
    try:
        with open(filepath, "r") as f:
            nb = json.load(f)
    except json.JSONDecodeError:
        errors.append(f"{filepath} - could not parse notebook as JSON")
        return errors

    for cell_idx, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        for line_num, line in enumerate(source.splitlines(), start=1):
            for match in PLACEHOLDER_PATTERN.finditer(line):
                errors.append(
                    f"{filepath} - cell {cell_idx + 1}, line {line_num}: "
                    f"unreplaced placeholder '{match.group()}' found"
                )
    return errors


def main():
    if not DELIVERY_DIR.exists():
        print("No delivery/ directory found. Skipping config check.")
        sys.exit(0)

    config_files = find_config_files(DELIVERY_DIR)

    if not config_files:
        print("No config files found in delivery/. Skipping config check.")
        sys.exit(0)

    all_errors = []
    for filepath in config_files:
        if filepath.suffix == ".ipynb":
            all_errors.extend(check_notebook_file(filepath))
        else:
            all_errors.extend(check_text_file(filepath))

    if all_errors:
        print("Unreplaced config placeholders found:")
        for error in all_errors:
            print(f"  {error}")
        print(
            "\nReplace all YOUR_<SOMETHING> placeholders with real values "
            "before committing."
        )
        sys.exit(1)

    print(f"Config check passed for {len(config_files)} file(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
