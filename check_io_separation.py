#!/usr/bin/env python3
"""
Check that raw print() and input() statements only exist within io_manager (file or package module).
This enforces separation of concerns where all I/O operations should go through io_manager.
"""

import re
import sys
from pathlib import Path

# Directories to exclude from recursive scanning
EXCLUDED_DIRS = {
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".idea",
    ".vscode",
}


def is_in_io_manager(file_path: Path) -> bool:
    """
    Check if a file is io_manager.py or located inside an io_manager directory module.
    """
    if file_path.name == "io_manager.py":
        return True
    
    # Check if 'io_manager' is any of the parent directories
    return "io_manager" in file_path.parts[:-1]


def check_file(file_path: Path) -> list[tuple[int, str]]:
    """
    Check a Python file for raw print() and input() statements.
    Returns a list of (line_number, line_content) tuples for violations.
    """
    violations = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                stripped = line.strip()

                # Skip empty lines and full-line comments
                if not stripped or stripped.startswith("#"):
                    continue

                # Remove inline comments to avoid flagging commented-out code
                code_part = line.split("#")[0]

                # Check for print() - but not print_update, print_error, def print_, .print, etc.
                if re.search(r"(?<!def\s)(?<!\.)(?<!_)\bprint\s*\(", code_part):
                    violations.append((line_num, line.rstrip()))

                # Check for input() - but not as part of another identifier
                if re.search(r"(?<!def\s)(?<!\.)(?<!_)\binput\s*\(", code_part):
                    violations.append((line_num, line.rstrip()))

    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []

    return violations


def main():
    """
    Recursively check all Python files in the project except:
    - io_manager.py or any files under io_manager/ directory
    - test_*.py files and files within test/ directories
    - Virtual environment and system directories
    - This script itself
    """
    script_path = Path(__file__).resolve()
    root_dir = Path(".")

    # Gather all .py files recursively
    py_files = [
        f for f in root_dir.rglob("*.py")
        if not any(part in EXCLUDED_DIRS for part in f.parts)
    ]

    # Filter out files where print/input are allowed
    files_to_check = [
        f for f in py_files
        if not is_in_io_manager(f)
        and not f.name.startswith("test_")
        and f.resolve() != script_path
    ]

    total_violations = 0
    files_with_violations = []

    print("Checking for raw print() and input() statements outside io_manager...")
    print(f"Checking {len(files_to_check)} file(s)...\n")

    for file_path in sorted(files_to_check):
        violations = check_file(file_path)

        if violations:
            total_violations += len(violations)
            files_with_violations.append(str(file_path))

            print(f"FAIL: {file_path}:")
            for line_num, line_content in violations:
                print(f"   Line {line_num}: {line_content}")
            print()

    if total_violations > 0:
        print(
            f"Found {total_violations} violation(s) in {len(files_with_violations)} file(s)."
        )
        print("\nWARNING: All print() and input() statements should be in io_manager")
        print(
            "   Use io_manager.print_update(), io_manager.print_error(), etc. instead"
        )
        sys.exit(1)
    else:
        print(
            "PASS: All checks passed! No raw print() or input() statements found outside io_manager."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()