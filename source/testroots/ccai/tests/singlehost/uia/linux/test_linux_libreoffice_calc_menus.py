import platform
import shutil

from ccai import testbase
from ccai.errors.exceptions import SkipError
from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.wrappers.uiawindow import LinuxWindow
from ccai.uia.platforms.linux.wrappers.dialogelement import LinuxSaveAsDialog, LinuxModalDialogFileAlreadyExists
from ccai.uia.platforms.linux.mappings.libreoffice_calc import LibreOfficeCalc
import time
import os
import subprocess
import shlex

def _open_save_as_dialog(app, main_window):
    """Refactored helper to open Save As dialog robustly."""
    print("Opening Save As dialog via menu clicks...")
    try:
        # 1. Click File Menu
        file_menu = LibreOfficeCalc.MenuBar.File.resolve(main_window)
        if not file_menu:
             print("File menu not found via hint, trying deep search...")
             # Fallback
             file_menu = main_window.find_element(name="File", role="menu")
        
        if file_menu:
             print(f"File Menu Bounds: {file_menu.bounds}")
             
             save_as_item = None
             menu_open_success = False
             
             # Retry loop to OPEN the menu
             for attempt in range(3):
                 print(f"Attempt {attempt+1}: Clicking File menu...")
                 # Force WM click
                 if file_menu.wm_agent:
                     x, y, w, h = file_menu.bounds
                     if x > 0 and w > 0:
                         file_menu.wm_agent.click(x + w//2, y + h//2)
                     else:
                         file_menu.click()
                 else:
                     file_menu.click()
                     
                 time.sleep(2.0)
                 
                 # Check if menu successfully opened by looking for Save As with valid bounds
                 save_as_item = file_menu.find_element(name="Save As...", role="menu item")
                 if not save_as_item:
                      save_as_item = file_menu.find_element(name="Save As", role="menu item")
                 
                 if save_as_item:
                     sx, sy, sw, sh = save_as_item.bounds
                     if sx > 0 and sw > 0:
                         print("Menu opened successfully (Save As is visible).")
                         menu_open_success = True
                         break
                     else:
                         print(f"Menu item found but has invalid bounds: {sx},{sy}. Menu not open?")
                 else:
                     print("Save As item not found in tree.")
             
             if not menu_open_success:
                 print("Clicking File menu failed to open menu (invalid bounds). Trying Alt+F fallback...")
                 if main_window.wm_agent:
                     main_window.wm_agent.send_keys(None, "%f")
                 else:
                     main_window.type_keys("%f")
                 time.sleep(2.0)
                 
                 # Last check
                 save_as_item = file_menu.find_element(name="Save As...", role="menu item")
                 if not save_as_item: save_as_item = file_menu.find_element(name="Save As", role="menu item")
                 
             if save_as_item:
                 # Check visibility and bounds
                 print(f"Found Save As item. Checking bounds...")
                 x, y, w, h = save_as_item.bounds
                 print(f"Bounds: {x}, {y}, {w}, {h}")
                 
                 # Force click using WM agent
                 if save_as_item.wm_agent and x > 0 and w > 0:
                     print(f"Force clicking Save As item at {x+w//2}, {y+h//2}")
                     save_as_item.wm_agent.click(x+w//2, y+h//2)
                 else:
                     print("Bounds invalid (Menu Item likely not mapped). Using Mnemonic fallback.")
                     # Since we successfully opened the File menu, typing the mnemonic 'a' 
                     # should trigger 'Save As...'
                     print("Sending mnemonic 'a'...")
                     main_window.type_keys("a")
                     
                 time.sleep(3)
                 
                 # Check if dialog appeared immediately
                 found_dialog = False
                 for w in app.get_windows():
                     if "Save As" in w.title:
                         found_dialog = True
                         break
                 
                 if not found_dialog:
                     print("DEBUG: Standard click didn't open dialog. Trying forced WM click...")
                     try:
                         # Force WM click using bounds
                         x, y, w, h = save_as_item.bounds
                         # Ensure valid bounds
                         if x > 0 and w > 0:
                             cx = x + (w // 2)
                             cy = y + (h // 2)
                             print(f"DEBUG: Forcing click at: {cx}, {cy}")
                             if save_as_item.wm_agent:
                                 save_as_item.wm_agent.click(cx, cy)
                                 time.sleep(3)
                         else:
                             print(f"DEBUG: Cannot force click, bounds invalid: {x},{y}")
                     except Exception as e:
                         print(f"DEBUG: Forced click failed: {e}")
             else:
                 print("Save As menu item not found.")
                 return None
        else:
             print("File menu not found.")
             return None

        # Search for dialog - check windows first to avoid deep scan
        dlg = None
        for _ in range(5):
            for w in app.get_windows():
                if "Save As" in w.title:
                     print(f"DEBUG: Found Save As window via get_windows: {w.title}")
                     from ccai.uia.platforms.linux.wrappers.dialogelement import LinuxSaveAsDialog
                     return LinuxSaveAsDialog(w.native_obj, w.access_agent, w.wm_agent)
            time.sleep(1.0)
        
        # Should not need deep scan if click worked.
        print("DEBUG: Dialog not found in top-level windows.")
        return None
        
    except Exception as e:
        print(f"Menu interaction failed: {e}")
        return None

def test_libreoffice_calc_menus_refactored():
    """
    Tests the "File -> Save As" menu flow using declarative mappings.
    Ensures the file is deleted beforehand to avoid "File Already Exists" dialog in this test.
    """
    if platform.system() != "Linux":
        return

    if shutil.which("libreoffice") is None:
        raise SkipError("libreoffice is not installed on this host")

    automation = AutomationFactory.get_automation_engine()
    
    # 1. Launch/Attach
    app = LibreOfficeCalc.launch_or_attach(automation)
    
    # 2. Get Main Window
    main_window = None
    for _ in range(10):
        main_window = LibreOfficeCalc.MainWindow.resolve(app)
        if main_window: break
        time.sleep(2)
        
    testbase.assert_equal(main_window is not None, True, "Main window not found")
    print(f"Main Window: {main_window.name}")
    
    # Ensure window is active
    main_window.activate()
    
    # Define filename
    timestamp = int(time.time())
    temp_filename = os.path.abspath(f"test_calc_menus_{timestamp}.ods")
    
    # Cleanup before test
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
        print(f"Deleted existing file: {temp_filename}")

    try:
        # 3. Open Save As Dialog
        save_dialog_window = _open_save_as_dialog(app, main_window)
        testbase.assert_equal(save_dialog_window is not None, True, "Save As dialog not found")
        
        if save_dialog_window:
            print(f"DEBUG: SaveAs Dialog found: {save_dialog_window}")
            
            # Find input using hint or fallback logic
            filename_input = LibreOfficeCalc.SaveAs.FileNameInput.resolve(save_dialog_window)
            if not filename_input:
                 filename_input = LibreOfficeCalc.SaveAs.FileNameEntry.resolve(save_dialog_window)

            if filename_input:
                filename_input.click()
                time.sleep(0.5)
                filename_input.type_keys(temp_filename)
            else:
                # Fallback to window typing
                print("DEBUG: Filename Input not found! typing to window.")
                save_dialog_window.type_keys(temp_filename)
            
            time.sleep(1)

            save_button = LibreOfficeCalc.SaveAs.SaveButton.resolve(save_dialog_window)
            if save_button:
                save_button.click()
            else:
                print(f"DEBUG: Save Button not found! Sending Enter.")
                save_dialog_window.type_keys("\n")
                
            time.sleep(3)
            
            # Check for unexpected confirmation dialog (dismiss if found)
            confirm_hint = LibreOfficeCalc.ConfirmOverwrite
            confirm_dialog = None
            for w in app.get_windows():
                 if confirm_hint.name in w.title or "Exist" in w.title or "Question" in w.title or "Confirm" in w.title:
                     confirm_dialog = w
                     break
            
            if confirm_dialog:
                 print("WARNING: Unexpected Confirmation Dialog Appeared! Attempting to dismiss.")
                 yes_btn = LibreOfficeCalc.ConfirmOverwrite.YesButton.resolve(confirm_dialog)
                 if yes_btn: yes_btn.click()
                 time.sleep(2)

        # 5. Verification
        print(f"Saving to: {temp_filename}")
        time.sleep(2)
        exists = os.path.exists(temp_filename)
        testbase.assert_equal(exists, True, "File was not verified on disk")
        
    finally:
        # Cleanup file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        # No app kill here, letting next test re-use or re-attach logic handle it.
        # But if we don't close, next test might get same window.
        # Let's try to close window? or just exit app.
        try:
             # Try Alt+F4 or similar?
             # Or rely on next test finding existing window.
             pass
        except Exception:
            pass


def test_libreoffice_calc_save_overwrite():
    """
    Tests the "File -> Save As" menu flow where the file ALREADY EXISTS.
    Verifies that the "Confirm Overwrite" dialog appears and is handled correctly.
    """
    if platform.system() != "Linux":
        return

    if shutil.which("libreoffice") is None:
        raise SkipError("libreoffice is not installed on this host")

    automation = AutomationFactory.get_automation_engine()
    # 1. Launch/Attach
    app = LibreOfficeCalc.launch_or_attach(automation)
    
    main_window = None
    for _ in range(10):
        main_window = LibreOfficeCalc.MainWindow.resolve(app)
        if main_window: break
        time.sleep(2)

    if main_window:
        main_window.activate()

    # 2. Create the file ahead of time
    timestamp = int(time.time()) + 1 # Different timestamp
    temp_filename = os.path.abspath(f"test_calc_overwrite_{timestamp}.ods")
    
    with open(temp_filename, "w") as f:
        f.write("dummy content")
    print(f"Created dummy file: {temp_filename}")

    try:
        # 3. File -> Save As
        save_dialog_window = _open_save_as_dialog(app, main_window)
        testbase.assert_equal(save_dialog_window is not None, True, "Save As dialog not found")
        
        # 4. Type existing filename
        if save_dialog_window:
            filename_input = LibreOfficeCalc.SaveAs.FileNameInput.resolve(save_dialog_window)
            if not filename_input:
                 filename_input = LibreOfficeCalc.SaveAs.FileNameEntry.resolve(save_dialog_window)

            if filename_input:
                filename_input.click()
                time.sleep(0.5)
                filename_input.type_keys(temp_filename)
            else:
                save_dialog_window.type_keys(temp_filename)
            
            time.sleep(1)

            save_button = LibreOfficeCalc.SaveAs.SaveButton.resolve(save_dialog_window)
            if save_button:
                save_button.click()
            else:
                save_dialog_window.type_keys("\n")
                
            time.sleep(2)
            
            # 5. Handle Confirmation Dialog (EXPECTED)
            print("Waiting for Confirmation Dialog...")
            confirm_dialog = None
            
            for _ in range(5):
                # Search windows and alerts
                for w in app.get_windows():
                     if "Question" in w.title or "Confirm" in w.title or "Exist" in w.title:
                         confirm_dialog = w
                         break
                
                if not confirm_dialog:
                     # Check alert children manually via agent if get_windows misses them
                     try:
                         children = app.access_agent.get_children(app.native_obj)
                         for child in children:
                             name = app.access_agent.get_name(child)
                             if name in ["Question", "Confirm", "Warning"]:
                                 from ccai.uia.platforms.linux.wrappers.uiawindow import LinuxWindow
                                 confirm_dialog = LinuxWindow(child, app.access_agent, app.wm_agent)
                                 break
                     except: pass

                if confirm_dialog: break
                time.sleep(1)
            
            testbase.assert_equal(confirm_dialog is not None, True, "Confirmation dialog did not appear")
            print(f"Confirmation Dialog Found: {confirm_dialog}")
            
            # Click Yes/Replace
            # Try finding Yes button
            yes_btn = LibreOfficeCalc.ConfirmOverwrite.YesButton.resolve(confirm_dialog)
            
            # Fallback if specific hint fails
            if not yes_btn:
                 yes_btn = confirm_dialog.find_element(role="push button", name="Yes")
            
            testbase.assert_equal(yes_btn is not None, True, "Yes button not found in confirmation dialog")
            yes_btn.click()
            time.sleep(3)
            
            # Verification
            exists = os.path.exists(temp_filename)
            testbase.assert_equal(exists, True, "File verification failed after overwrite")
            
            size = os.path.getsize(temp_filename)
            print(f"File size after overwrite: {size}")
            testbase.assert_equal(size > 20, True, "File seems to be the dummy file, verification failed")

    finally:
        if os.path.exists(temp_filename):
            # os.remove(temp_filename) # Keep for inspection? or remove? Remove to keep clean.
            os.remove(temp_filename)
        
        # Kill the app process if possible
        # Since we use subprocess in launch_or_attach, we can't kill easily unless we return handle.
        # subprocess.run(["killall", "soffice"]) ?
        # Be careful not to kill user's real open docs if they have any (but we asked them to close).
        try:
             subprocess.run(["pkill", "soffice"])
        except: pass

if __name__ == "__main__":
    test_libreoffice_calc_menus_refactored()
    # Wait for app to close/reset? actually we re-use.
    time.sleep(2)
    test_libreoffice_calc_save_overwrite()
