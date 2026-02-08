#!/usr/bin/env python3
"""
Verification script for video module implementation.

Checks that all files exist, have proper structure, and follow patterns.
Does not require external dependencies to be installed.
"""

import ast
import sys
from pathlib import Path


def check_file_exists(path: Path) -> bool:
    """Check if file exists."""
    if not path.exists():
        print(f"[FAIL] Missing: {path}")
        return False
    print(f"[PASS] Found: {path}")
    return True


def check_python_syntax(path: Path) -> bool:
    """Check if Python file has valid syntax."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            ast.parse(f.read())
        print(f"[PASS] Valid syntax: {path.name}")
        return True
    except SyntaxError as e:
        print(f"[FAIL] Syntax error in {path.name}: {e}")
        return False


def check_has_docstring(path: Path) -> bool:
    """Check if module has a docstring."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        if ast.get_docstring(tree):
            print(f"[PASS] Has docstring: {path.name}")
            return True
        else:
            print(f"[WARN] Missing module docstring: {path.name}")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking docstring in {path.name}: {e}")
        return False


def check_class_exists(path: Path, class_name: str) -> bool:
    """Check if a class exists in the file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                print(f"[PASS] Found class: {class_name} in {path.name}")
                return True

        print(f"[FAIL] Missing class: {class_name} in {path.name}")
        return False
    except Exception as e:
        print(f"[FAIL] Error checking class in {path.name}: {e}")
        return False


def main():
    """Run verification checks."""
    print("=" * 70)
    print("Video Module Verification")
    print("=" * 70)

    base_dir = Path(__file__).parent / "src" / "video"

    checks_passed = 0
    checks_failed = 0

    # Check file existence
    print("\n[1] Checking file structure...")
    files = [
        base_dir / "__init__.py",
        base_dir / "interfaces.py",
        base_dir / "lipsync.py",
        base_dir / "encoder.py",
    ]

    for file in files:
        if check_file_exists(file):
            checks_passed += 1
        else:
            checks_failed += 1

    # Check Python syntax
    print("\n[2] Checking Python syntax...")
    for file in files:
        if file.exists():
            if check_python_syntax(file):
                checks_passed += 1
            else:
                checks_failed += 1

    # Check module docstrings
    print("\n[3] Checking module docstrings...")
    for file in files:
        if file.exists():
            if check_has_docstring(file):
                checks_passed += 1
            # Docstring is optional, don't fail

    # Check required classes
    print("\n[4] Checking required classes...")
    class_checks = [
        (base_dir / "interfaces.py", "LipSyncConfig"),
        (base_dir / "interfaces.py", "LipSyncResult"),
        (base_dir / "interfaces.py", "EncodingConfig"),
        (base_dir / "interfaces.py", "EncodingResult"),
        (base_dir / "interfaces.py", "LipSyncEngineInterface"),
        (base_dir / "interfaces.py", "VideoEncoderInterface"),
        (base_dir / "lipsync.py", "MuseTalkLipSync"),
        (base_dir / "encoder.py", "FFmpegEncoder"),
    ]

    for file, class_name in class_checks:
        if file.exists():
            if check_class_exists(file, class_name):
                checks_passed += 1
            else:
                checks_failed += 1

    # Check CLI integration
    print("\n[5] Checking CLI integration...")
    cli_file = Path(__file__).parent / "src" / "cli.py"
    if cli_file.exists():
        with open(cli_file, "r", encoding="utf-8") as f:
            cli_content = f.read()

        required_imports = [
            "from .video import",
            "MuseTalkLipSync",
            "FFmpegEncoder",
        ]

        required_commands = [
            "def lipsync(",
            "def encode(",
            "def info(",
        ]

        for import_stmt in required_imports:
            if import_stmt in cli_content:
                print(f"[PASS] CLI import: {import_stmt}")
                checks_passed += 1
            else:
                print(f"[FAIL] Missing CLI import: {import_stmt}")
                checks_failed += 1

        for command in required_commands:
            if command in cli_content:
                print(f"[PASS] CLI command: {command}")
                checks_passed += 1
            else:
                print(f"[FAIL] Missing CLI command: {command}")
                checks_failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    print(f"Checks passed: {checks_passed}")
    print(f"Checks failed: {checks_failed}")

    if checks_failed == 0:
        print("\n[SUCCESS] All verification checks passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install FFmpeg: https://ffmpeg.org/download.html")
        print("3. Test CLI: avatar video --help")
        return 0
    else:
        print("\n[FAILED] Some verification checks failed.")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
