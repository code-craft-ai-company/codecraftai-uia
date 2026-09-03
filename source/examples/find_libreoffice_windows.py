#!/usr/bin/env python3
"""
Simple diagnostic script to find LibreOffice windows using AT-SPI
Run this with LibreOffice Calc already open
"""

import sys

def main():
    print("=" * 60)
    print("LibreOffice Window Finder - Diagnostic Script")
    print("=" * 60)
    print()
    
    # Step 1: Import pyatspi
    print("Step 1: Importing pyatspi...")
    try:
        import pyatspi
        print("✅ pyatspi imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pyatspi: {e}")
        return 1
    
    # Step 2: Get desktop
    print("\nStep 2: Getting AT-SPI desktop...")
    try:
        desktop = pyatspi.Registry.getDesktop(0)
        print(f"✅ Desktop obtained: {desktop}")
    except Exception as e:
        print(f"❌ Failed to get desktop: {e}")
        return 1
    
    # Step 3: Search for LibreOffice application
    print("\nStep 3: Searching for LibreOffice application...")
    app = None
    app_count = desktop.childCount
    print(f"   Found {app_count} applications")
    
    for i in range(app_count):
        try:
            child = desktop.getChildAtIndex(i)
            app_name = child.name
            print(f"   [{i}] Application: '{app_name}'")
            
            # Look for LibreOffice variants
            if app_name and any(name in app_name.lower() for name in ["soffice", "libreoffice", "calc"]):
                app = child
                print(f"   ✅ Found LibreOffice app: '{app_name}'")
                break
        except Exception as e:
            print(f"   ⚠️  Error accessing app {i}: {e}")
            continue
    
    if not app:
        print("\n❌ LibreOffice application not found!")
        print("   Make sure LibreOffice Calc is running")
        return 1
    
    # Step 4: Get windows
    print(f"\nStep 4: Getting windows from '{app.name}'...")
    window_count = app.childCount
    print(f"   Application has {window_count} children")
    
    windows = []
    for i in range(window_count):
        try:
            child = app.getChildAtIndex(i)
            role = child.getRole()
            role_name = child.getRoleName()
            child_name = child.name
            
            print(f"   [{i}] Role: {role_name} ({role}), Name: '{child_name}'")
            
            if role == pyatspi.ROLE_FRAME:
                windows.append(child)
                print(f"      ✅ This is a window!")
        except Exception as e:
            print(f"   ⚠️  Error accessing child {i}: {e}")
            continue
    
    if not windows:
        print("\n❌ No windows found!")
        return 1
    
    print(f"\n✅ Found {len(windows)} window(s)")
    
    # Step 5: Display window details
    print("\nStep 5: Window details...")
    for idx, win in enumerate(windows):
        print(f"\n--- Window {idx + 1} ---")
        print(f"   Name: {win.name}")
        print(f"   Role: {win.getRoleName()}")
        
        try:
            states = win.getState()
            print(f"   States: {states}")
        except Exception:
            print("   States: (unable to get)")
        
        try:
            component = win.queryComponent()
            x, y, width, height = component.getExtents(pyatspi.DESKTOP_COORDS)
            print(f"   Position: ({x}, {y})")
            print(f"   Size: {width}x{height}")
        except Exception:
            print("   Position/Size: (unable to get)")
    
    # Step 6: Test focus
    print("\nStep 6: Testing focus on first window...")
    test_window = windows[0]
    print(f"   Attempting to grab focus on: {test_window.name}")
    
    try:
        component = test_window.queryComponent()
        result = component.grabFocus()
        print(f"   ✅ grabFocus() returned: {result}")
        
        import time
        time.sleep(0.5)
        
        # Check if it has focus
        states = test_window.getState()
        has_focus = states.contains(pyatspi.STATE_ACTIVE)
        print(f"   Window is active: {has_focus}")
        
    except Exception as e:
        print(f"   ❌ Error grabbing focus: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic complete!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
