#!/usr/bin/env python3
"""
Simple script to rename the original main.py to old_main.py
"""
import os
import shutil
import sys

def rename_main():
    """Rename main.py to old_main.py if it exists."""
    if os.path.exists('main.py'):
        print("Renaming main.py to old_main.py")
        shutil.move('main.py', 'old_main.py')
        print("Done!")
    else:
        print("main.py not found")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(rename_main()) 