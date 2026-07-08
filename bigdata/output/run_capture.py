#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Execute analyze_data.py and capture all output to a file."""
import subprocess
import sys
import os

os.chdir(r'D:\OneDrive\桌面\bigdata')
result = subprocess.run(
    [sys.executable, r'D:\OneDrive\桌面\bigdata\analyze_data.py'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    timeout=120
)
output_path = r'D:\OneDrive\桌面\bigdata\output\captured_output.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("=== STDOUT ===\n")
    f.write(result.stdout)
    f.write("\n=== STDERR ===\n")
    f.write(result.stderr)
    f.write(f"\n=== RETURN CODE: {result.returncode} ===\n")
print(f"Output captured to: {output_path}")
print(f"Return code: {result.returncode}")
print(f"Stdout length: {len(result.stdout)}")
print(f"Stderr length: {len(result.stderr)}")
