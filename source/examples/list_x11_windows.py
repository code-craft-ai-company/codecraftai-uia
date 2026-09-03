#!/usr/bin/env python3
import subprocess
import time
from Xlib import X, display

# Launch LibreOffice if not already running
try:
    proc = subprocess.Popen(["libreoffice", "--calc"])
    time.sleep(5)
except Exception:
    proc = None

# Connect to X11
d = display.Display()
root = d.screen().root

def get_window_name(window):
    try:
        return window.get_wm_name()
    except Exception:
        return None

def get_window_class(window):
    try:
        wm_class = window.get_wm_class()
        return wm_class if wm_class else None
    except Exception:
        return None

def list_windows(win, depth=0):
    """Recursively list all windows"""
    if depth > 5:
        return
    
    name = get_window_name(win)
    wm_class = get_window_class(win)
    
    if name or wm_class:
        print(f"{'  ' * depth}Window ID: {win.id}")
        print(f"{'  ' * depth}  Name: {name}")
        print(f"{'  ' * depth}  Class: {wm_class}")
    
    try:
        children = win.query_tree().children
        for child in children:
            list_windows(child, depth + 1)
    except Exception:
        pass

print("Listing all X11 windows:\n")
list_windows(root)

if proc:
    proc.terminate()
