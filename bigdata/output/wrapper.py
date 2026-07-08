#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WRAPPER: Run analyze_data.py and capture ALL output to captured_output.txt
Run this manually: python D:\OneDrive\桌面\bigdata\output\wrapper.py
"""
import subprocess, sys, os

DATA_DIR = r'D:\OneDrive\桌面\bigdata'
os.chdir(DATA_DIR)

result = subprocess.run(
    [sys.executable, os.path.join(DATA_DIR, 'analyze_data.py')],
    capture_output=True, text=True, encoding='utf-8', timeout=120
)

outpath = os.path.join(DATA_DIR, 'output', 'captured_output.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(result.stdout)
    if result.stderr:
        f.write('\n\n=== STDERR ===\n')
        f.write(result.stderr)
    f.write(f'\n\n=== EXIT CODE: {result.returncode} ===')

# Also print to console so user can see it immediately
print(result.stdout)
if result.stderr:
    print('\n=== STDERR ===')
    print(result.stderr)
print(f'\n[Output also saved to: {outpath}]')
print(f'[Total stdout chars: {len(result.stdout)}]')
