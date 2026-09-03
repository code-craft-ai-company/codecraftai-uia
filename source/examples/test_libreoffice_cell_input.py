#!/usr/bin/env python3
"""
Test if double-clicking a cell enables keyboard input in LibreOffice Calc
Run with LibreOffice Calc already open
"""
import sys
import time
sys.path.insert(0, '/home/myron/repos/codecraftai-uia/source/packages')

from ccai.uia.factory import AutomationFactory

def find_first_cell(element, depth=0):
    """Recursively find the first table cell"""
    if depth > 15:
        return None
    
    try:
        role_name = element.role_name
        if role_name == "table cell":
            return element
        
        count = element._native_obj.childCount
        for i in range(min(count, 50)):
            child = element._native_obj.getChildAtIndex(i)
            from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement
            child_element = LinuxElement(child, element._access_agent, element._wm_agent)
            result = find_first_cell(child_element, depth + 1)
            if result:
                return result
    except Exception:
        pass
    
    return None

def main():
    print("Finding LibreOffice Calc...")
    automation = AutomationFactory.get_automation_engine()
    
    app = automation.get_application_by_name("soffice")
    if not app:
        print("ERROR: LibreOffice not found!")
        return 1
    
    windows = app.get_windows()
    if not windows:
        print("ERROR: No windows found!")
        return 1
    
    window = windows[0]
    print(f"Found window: {window.title}")
    
    print("\nActivating window...")
    window.activate()
    time.sleep(1)
    
    print("\nFinding first cell...")
    cell = find_first_cell(window)
    if not cell:
        print("ERROR: No cell found!")
        return 1
    
    print(f"Found cell: {cell.name}")
    
    # Test 1: Single click + type
    print("\n--- Test 1: Single Click + Type ---")
    cell.click()
    time.sleep(0.3)
    cell.grab_focus()
    time.sleep(0.2)
    cell.type_keys("TEST1")
    time.sleep(0.5)
    print("Typed: TEST1")
    
    # Test 2: Double click + type
    print("\n--- Test 2: Double Click + Type ---")
    cell.click()
    time.sleep(0.1)
    cell.click()  # Second click
    time.sleep(0.3)
    cell.type_keys("TEST2")
    time.sleep(0.5)
    print("Typed: TEST2")
    
    # Test 3: Click + F2 + type
    print("\n--- Test 3: Click + F2 + Type ---")
    cell.click()
    time.sleep(0.3)
    cell.grab_focus()
    time.sleep(0.2)
    # Type F2 to enter edit mode  
    cell.type_keys("f2")  # Lowercase as per keymap
    time.sleep(0.3)
    cell.type_keys("TEST3")
    time.sleep(0.5)
    print("Typed: F2, then TEST3")
    
    print("\n✅ Test complete! Check LibreOffice to see which method worked.")
    print("If a cell has 'TEST1', 'TEST2', or 'TEST3', that method works!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
