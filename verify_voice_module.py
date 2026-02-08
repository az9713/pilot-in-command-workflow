#!/usr/bin/env python3
"""
Voice module verification script.

Verifies the voice module structure without requiring external dependencies.
"""

import ast
import sys
from pathlib import Path

def check_syntax(file_path: Path) -> bool:
    """Check if Python file has valid syntax."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return False

def main():
    """Verify voice module implementation."""
    print("=" * 70)
    print("Voice Module Verification")
    print("=" * 70)

    voice_dir = Path("src/voice")

    if not voice_dir.exists():
        print(f"Error: {voice_dir} not found")
        sys.exit(1)

    # Check all Python files
    files = [
        "interfaces.py",
        "profiles.py",
        "cloner.py",
        "synthesizer.py",
        "__init__.py",
    ]

    print("\n[File Structure]")
    all_valid = True

    for filename in files:
        filepath = voice_dir / filename
        if not filepath.exists():
            print(f"  Missing: {filename}")
            all_valid = False
            continue

        lines = len(filepath.read_text(encoding="utf-8").splitlines())
        syntax_ok = check_syntax(filepath)
        status = "OK" if syntax_ok else "SYNTAX ERROR"
        print(f"  {filename:20s} {lines:4d} lines - {status}")

        if not syntax_ok:
            all_valid = False

    # Check CLI integration
    print("\n[CLI Integration]")
    cli_file = Path("src/cli.py")

    if not cli_file.exists():
        print("  CLI file not found")
        all_valid = False
    else:
        cli_content = cli_file.read_text(encoding="utf-8")

        checks = [
            ("Voice import", "from .voice import"),
            ("Voice group", "@main.group()\ndef voice():"),
            ("Clone command", "@voice.command()\n@click.argument(\"audio_file\""),
            ("Speak command", "def speak(text: str, profile: str"),
            ("List command", "@voice.command(\"list\")"),
        ]

        for check_name, check_pattern in checks:
            if check_pattern in cli_content:
                print(f"  {check_name:30s} Found")
            else:
                print(f"  {check_name:30s} MISSING")
                all_valid = False

    # Check interfaces
    print("\n[Interface Definitions]")
    interfaces_file = voice_dir / "interfaces.py"

    if interfaces_file.exists():
        content = interfaces_file.read_text(encoding="utf-8")

        interfaces = [
            "VoiceProfile",
            "CloneResult",
            "SynthesisResult",
            "VoiceClonerInterface",
            "TTSSynthesizerInterface",
        ]

        for interface in interfaces:
            if f"class {interface}" in content or f"def {interface}" in content:
                print(f"  {interface:30s} Defined")
            else:
                print(f"  {interface:30s} MISSING")
                all_valid = False

    # Check implementations
    print("\n[Implementations]")

    implementations = [
        ("XTTSVoiceCloner", "cloner.py"),
        ("CoquiTTSSynthesizer", "synthesizer.py"),
        ("VoiceProfileManager", "profiles.py"),
    ]

    for class_name, filename in implementations:
        filepath = voice_dir / filename
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            if f"class {class_name}" in content:
                print(f"  {class_name:30s} Implemented")
            else:
                print(f"  {class_name:30s} MISSING")
                all_valid = False

    # Summary
    print("\n" + "=" * 70)
    if all_valid:
        print("Status: All checks passed")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -e .")
        print("  2. Test voice commands: avatar voice --help")
        print("  3. Clone a voice: avatar voice clone audio.wav --name 'Test'")
        print("  4. List profiles: avatar voice list")
        print("  5. Synthesize speech: avatar voice speak 'Hello' --profile ID --output out.wav")
        sys.exit(0)
    else:
        print("Status: Some checks failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
