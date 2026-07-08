#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read raw .dat files and output first few lines for inspection."""
import os

DATA_DIR = r'D:\OneDrive\桌面\bigdata'
files = ['host_detail.dat', 'mod_detail.dat', 'disk_tsar.dat', 'pref_tsar.dat']

for fname in files:
    fpath = os.path.join(DATA_DIR, fname)
    print(f"\n{'='*60}")
    print(f"File: {fname}")
    print(f"Size: {os.path.getsize(fpath)} bytes")
    print(f"{'='*60}")
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 8:
                    print(f"... (truncated, {i+1} lines read so far)")
                    break
                print(f"  Line {i+1}: {repr(line[:200])}")
    except UnicodeDecodeError:
        with open(fpath, 'r', encoding='gbk') as f:
            for i, line in enumerate(f):
                if i >= 8:
                    print(f"... (truncated, {i+1} lines read so far)")
                    break
                print(f"  Line {i+1}: {repr(line[:200])}")
    except Exception as e:
        print(f"  Error: {e}")
