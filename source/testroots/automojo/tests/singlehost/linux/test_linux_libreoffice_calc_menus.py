from automojo import testbase
from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.wrappers.uiawindow import LinuxWindow
from automojo.uia.platforms.linux.wrappers.dialogelement import LinuxSaveAsDialog, LinuxModalDialogFileAlreadyExists
import time
import os
import subprocess
import shlex

def test_libreoffice_calc_menus_refactored():
    automation = AutomationFactory.get_automation_engine()
    
    # 1. Launch/Find App
    # Declarative Usage
    from automojo.uia.platforms.linux.mappings.libreoffice_calc import LibreOfficeCalc
    
    # 1. Launch/Find App
    app = LibreOfficeCalc.attach(automation)
    
    launched_app = False
    if not app:
        print("LibreOffice Calc not running, launching...")
        subprocess.Popen(shlex.split("libreoffice --calc --norestore"))
        launched_app = True
        
        for _ in range(10):
            time.sleep(2)
            app = LibreOfficeCalc.attach(automation)
            if app:
                print(f"Launched App: {app}")
                break
    
    testbase.assert_equal(app is not None, True, "LibreOffice Calc should be running")

    try:
        # 2. Get Main Window
        # Wait for windows to appear
        main_window = None
        for _ in range(10):
            windows = app.get_windows()
            if len(windows) > 0:
                # Check for Document Recovery
                for w in windows:
                    if "Recovery" in w.title:
                        print("Found Document Recovery dialog, attempting to discard...")
                        # Try to find Discard button
                        discard = w.find_descendant(name="Discard")
                        if not discard: discard = w.find_descendant(name="Cancel")
                        if discard:
                            discard.click()
                            time.sleep(2)
                            # Update windows list
                            windows = app.get_windows()
                
                # Pick the first non-recovery window matching hint if possible
                for w in windows:
                    # Naively match main window hint manually or just take first non-recovery
                    if "Recovery" not in w.title:
                        main_window = w
                        break
                
                if main_window: break
            time.sleep(1)
            
        testbase.assert_equal(main_window is not None, True, "No main window found")
        print(f"Main Window: {main_window.title}")
        
        main_window.activate()
        time.sleep(2)
        
        # 3. Menu Interaction
        menu_bar = main_window.main_menu
        # Note: mapping has MenuBar hint but we use standard prop for now
        
        testbase.assert_equal(menu_bar is not None, True, "Main Menu Bar not found")
        
        # Declarative Menu Item finding
        # Using hinting from the class if we can resolve it?
        # LibreOfficeCalc.MenuBar.File is an ElementHint("menu", "File")
        
        # Manually resolving the File menu using the hint
        file_menu_hint = LibreOfficeCalc.MenuBar.File
        file_menu = menu_bar.get_menu(file_menu_hint.name)
        
        testbase.assert_equal(file_menu is not None, True, "File menu not found")
        file_menu.open()
        time.sleep(1)
        
        # Save As Item
        save_as_hint = LibreOfficeCalc.SaveAsMenuItem
        save_as_item = file_menu.get_item(save_as_hint.name)
        if not save_as_item:
             # Fallback search matching hint name in items
             for item in file_menu.get_items():
                 if "Save As" in item.name:
                     save_as_item = item
                     break
        
        testbase.assert_equal(save_as_item is not None, True, "Save As item not found")
        save_as_item.invoke()
        time.sleep(2)
        
        # 4. Handle Save Dialog using Declarative Mapping
        # Find the window matching the hint
        save_as_hint = LibreOfficeCalc.SaveAs
        
        save_dialog_window = None
        for _ in range(5):
            for w in app.get_windows():
                # manual match against hint
                # hint.name is "Save As", we check if title contains it
                if save_as_hint.name in w.title or "Save" in w.title:
                    save_dialog_window = w
                    break
            if save_dialog_window: break
            time.sleep(1)
            
        testbase.assert_equal(save_dialog_window is not None, True, "Save As dialog not found")
        
        # 5. Set Filename and Save using hints
        timestamp = int(time.time())
        temp_filename = os.path.abspath(f"test_refactored_{timestamp}.ods")
        print(f"Saving to: {temp_filename}")
        
        # Resolve children
        filename_input = LibreOfficeCalc.SaveAs.FileNameInput.resolve(save_dialog_window)
        if not filename_input:
             # Try entry fallback
             filename_input = LibreOfficeCalc.SaveAs.FileNameEntry.resolve(save_dialog_window)
             
        if filename_input:
            filename_input.click()
            time.sleep(0.5)
            filename_input.type_keys(temp_filename)
        else:
            # Fallback
            save_dialog_window.type_keys(temp_filename)
        
        time.sleep(1)
        
        save_button = LibreOfficeCalc.SaveAs.SaveButton.resolve(save_dialog_window)
        if save_button:
            save_button.click()
        else:
            save_dialog_window.type_keys("\n")
            
        time.sleep(3)
        
        # 6. Handle Confirmation (File Exists)
        confirm_hint = LibreOfficeCalc.ConfirmOverwrite
        confirm_dialog = None
        
        for _ in range(3):
            # Check windows
            for w in app.get_windows():
                if confirm_hint.name in w.title or "Exist" in w.title:
                    confirm_dialog = w
                    break
            
            # Check alerts (children of app) - existing logic preserved 
            if not confirm_dialog:
                 children = app.access_agent.get_children(app.native_obj)
                 for child in children:
                     try:
                         # name might be "Question"
                         if app.access_agent.get_name(child) == "Question":
                             confirm_dialog = LinuxWindow(child, app.access_agent, app.wm_agent)
                             break
                     except: pass
            
            if confirm_dialog: break
            time.sleep(1)
            
        if confirm_dialog:
            print(f"Handling Confirmation Dialog: {confirm_dialog.title}")
            
            # Resolve buttons using hints
            yes_btn = LibreOfficeCalc.ConfirmOverwrite.YesButton.resolve(confirm_dialog)
            if not yes_btn:
                 yes_btn = LibreOfficeCalc.ConfirmOverwrite.ReplaceButton.resolve(confirm_dialog)
            
            if yes_btn:
                yes_btn.click()
            time.sleep(3)
            
        # 7. Verification
        exists = os.path.exists(temp_filename)
        print(f"File exists: {exists}")
        if exists:
            os.remove(temp_filename)
            
        testbase.assert_equal(exists, True, "File was not verified on disk")

    finally:
        if launched_app:
            print("Closing application...")
            subprocess.run(["pkill", "soffice"])

if __name__ == "__main__":
    test_libreoffice_calc_menus_refactored()
