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
    app = automation.get_application_by_name("soffice")
    if not app:
        app = automation.get_application_by_name("Calc")
    
    launched_app = False
    if not app:
        print("LibreOffice Calc not running, launching...")
        subprocess.Popen(shlex.split("libreoffice --calc --norestore"))
        launched_app = True
        
        for _ in range(10):
            time.sleep(2)
            app = automation.get_application_by_name("soffice")
            if not app:
                app = automation.get_application_by_name("Calc")
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
                
                # Pick the first non-recovery window
                for w in windows:
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
        if not menu_bar:
            print("Menu bar not found. Dumping window children:")
            children = main_window.access_agent.get_children(main_window.native_obj)
            for child in children:
                try:
                    print(f" - {main_window.access_agent.get_role_name(child)}: {main_window.access_agent.get_name(child)}")
                except: pass
                
        testbase.assert_equal(menu_bar is not None, True, "Main Menu Bar not found")
        
        file_menu = menu_bar.get_menu("File")
        testbase.assert_equal(file_menu is not None, True, "File menu not found")
        file_menu.open()
        time.sleep(1)
        
        save_as_item = file_menu.get_item("Save As...")
        if not save_as_item:
             # Fallback search
             for item in file_menu.get_items():
                 if "Save As" in item.name:
                     save_as_item = item
                     break
        
        testbase.assert_equal(save_as_item is not None, True, "Save As item not found")
        save_as_item.invoke()
        time.sleep(2)
        
        # 4. Handle Save Dialog using new Class
        # Find the raw window first
        raw_dialog = None
        for _ in range(5):
            for w in app.get_windows():
                if "Save As" in w.title or "Save" in w.title:
                    raw_dialog = w
                    break
            if raw_dialog: break
            time.sleep(1)
            
        testbase.assert_equal(raw_dialog is not None, True, "Save As dialog not found")
        
        # Upgrade to LinuxSaveAsDialog
        save_dialog = LinuxSaveAsDialog(raw_dialog.native_obj, raw_dialog.access_agent, raw_dialog.wm_agent)
        
        # 5. Set Filename and Save
        timestamp = int(time.time())
        temp_filename = os.path.abspath(f"test_refactored_{timestamp}.ods")
        print(f"Saving to: {temp_filename}")
        
        save_dialog.set_filename(temp_filename)
        time.sleep(1)
        save_dialog.save()
        time.sleep(3)
        
        # 6. Handle Confirmation (File Exists) if needed
        # Check for alert dialog
        confirm_dialog = None
        for _ in range(3):
            # Check windows
            for w in app.get_windows():
                if "Confirm" in w.title or "Exist" in w.title:
                    confirm_dialog = w
                    break
            
            # Check alerts (children of app)
            if not confirm_dialog:
                 children = app.access_agent.get_children(app.native_obj)
                 for child in children:
                     try:
                         if app.access_agent.get_role(child) == 2 or app.access_agent.get_name(child) == "Question":
                             confirm_dialog = LinuxWindow(child, app.access_agent, app.wm_agent)
                             break
                     except: pass
            
            if confirm_dialog: break
            time.sleep(1)
            
        if confirm_dialog:
            print(f"Handling Confirmation Dialog: {confirm_dialog.title}")
            # Try to print text content of dialog to understand what it is
            try:
                print(f"Dialog Text: {confirm_dialog.text}")
            except: pass
            
            confirm_wrapper = LinuxModalDialogFileAlreadyExists(confirm_dialog.native_obj, confirm_dialog.access_agent, confirm_dialog.wm_agent)
            confirm_wrapper.confirm_overwrite()
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
