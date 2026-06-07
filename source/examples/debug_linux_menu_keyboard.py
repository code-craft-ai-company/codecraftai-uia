
import time
import sys
import os

# Add source to path for direct execution if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.mappings.libreoffice_calc import LibreOfficeCalc

def debug_menu_keyboard():
    print("Initializing Automation Engine...")
    automation = AutomationFactory.get_automation_engine()
    
    print("Attaching to LibreOffice Calc...")
    app = LibreOfficeCalc.launch_or_attach(automation)
    
    print("Resolving Main Window...")
    main_window = LibreOfficeCalc.MainWindow.resolve(app)
    
    if not main_window:
        print("Main window not found!")
        return

    print(f"Found Main Window: '{main_window.name}'")
    main_window.activate()
    time.sleep(1)

    print("Sending 'Alt+f' to open File menu...")
    # Using type_keys which usually handles basic mnemonics
    main_window.type_keys("%f")
    
    print("Waiting 2 seconds (Look for File menu opening)...")
    time.sleep(2)
    
    print("Sending 'a' for Save As...")
    main_window.type_keys("a")
    
    print("Waiting 2 seconds (Look for Save As dialog)...")
    time.sleep(2)
    
    # Verify if dialog appeared (optional logic, mainly visual check for user)
    # Simple bounds check on a potential dialog
    print("Done. Did the dialog appear?")

if __name__ == "__main__":
    debug_menu_keyboard()
