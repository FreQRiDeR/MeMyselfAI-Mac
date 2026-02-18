#!/usr/bin/env python3
"""
test_icon_path.py - Test what PyInstaller sees during build
"""

from pathlib import Path
import sys

print("=" * 60)
print("Icon Path Debug")
print("=" * 60)
print()

# Show current directory
print(f"Current directory: {Path.cwd()}")
print(f"Script location: {Path(__file__).parent}")
print()

# Check for icon
possible_paths = [
    'MeMyselfAi.icns',
    Path.cwd() / 'MeMyselfAi.icns',
    Path(__file__).parent / 'MeMyselfAi.icns',
]

print("Checking icon locations:")
for path in possible_paths:
    p = Path(path)
    exists = p.exists()
    print(f"  {'✅' if exists else '❌'} {path}")
    if exists:
        print(f"      Absolute: {p.absolute()}")
        print(f"      Size: {p.stat().st_size} bytes")

print()
print("Files in current directory:")
for f in Path.cwd().glob('*.icns'):
    print(f"  - {f.name} ({f.stat().st_size} bytes)")

print()
print("Files in script directory:")
for f in Path(__file__).parent.glob('*.icns'):
    print(f"  - {f.name} ({f.stat().st_size} bytes)")
