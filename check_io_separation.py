#!/usr/bin/env python3
"""
Check that raw print() and input() statements only exist in io_manager.py
This enforces separation of concerns where all I/O operations should go through io_manager
"""

import re
import sys
from pathlib import Path


def check_file(file_path: Path) -> list[tuple[int, str]]:
    """
    Check a Python file for raw print() and input() statements.
    Returns a list of (line_number, line_content) tuples for violations.
    """
    violations = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                stripped = line.strip()

                # Skip empty lines and full-line comments
                if not stripped or stripped.startswith('#'):
                    continue

                # Remove inline comments to avoid flagging commented-out code
                # Split by '#' and only check the code part (before the comment)
                code_part = line.split('#')[0]

                # Check for print() - but not print_update, print_error, print_shelter_list, etc.
                # Match: print( but not def print_ or .print or anything_print
                if re.search(r'(?<!def\s)(?<!\.)(?<!_)\bprint\s*\(', code_part):
                    violations.append((line_num, line.rstrip()))

                # Check for input() - but not as part of another identifier
                # Match: input( but not def input_ or .input or anything_input
                if re.search(r'(?<!def\s)(?<!\.)(?<!_)\binput\s*\(', code_part):
                    violations.append((line_num, line.rstrip()))

    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []

    return violations


def main():
    """
    Check all Python files in the current directory except:
    - io_manager.py (where print/input are allowed)
    - test_*.py files (tests may legitimately print for debugging)
    - Files in venv/ or other virtual environment directories
    """

    # Get all .py files in current directory only (not subdirectories)
    py_files = list(Path('.').glob('*.py'))

    # Filter out files where print/input are allowed
    files_to_check = [
        f for f in py_files
        if f.name != 'io_manager.py'
        and not f.name.startswith('test_')
        and f.name != 'check_io_separation.py'  # Don't check this script itself
    ]

    total_violations = 0
    files_with_violations = []

    print("Checking for raw print() and input() statements outside io_manager.py...")
    print(f"Files to check: {', '.join(f.name for f in files_to_check)}\n")

    for file_path in files_to_check:
        violations = check_file(file_path)

        if violations:
            total_violations += len(violations)
            files_with_violations.append(file_path.name)

            print(f"FAIL: {file_path.name}:")
            for line_num, line_content in violations:
                print(f"   Line {line_num}: {line_content}")
            print()

    if total_violations > 0:
        print(f"Found {total_violations} violation(s) in {len(files_with_violations)} file(s).")
        print("\nWARNING: All print() and input() statements should be in io_manager.py")
        print("   Use io_manager.print_update(), io_manager.print_error(), etc. instead")
        sys.exit(1)
    else:
        print("PASS: All checks passed! No raw print() or input() statements found outside io_manager.py")
        sys.exit(0)


if __name__ == "__main__":
    main()
