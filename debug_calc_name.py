

import subprocess
import time
import sys
import os

# Add source to path so we can import ccai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'source/packages')))

from ccai.uia.factory import AutomationFactory

def debug_calc_name():
    try:
        proc = subprocess.Popen(["gnome-calculator"])
        time.sleep(2.0)
        
        automation = AutomationFactory.get_automation_engine()
        
        # Dump all apps
        import pyatspi
        reg = pyatspi.Registry
        desktop = reg.getDesktop(0)
        print("--- Running Applications ---")
        for i in range(desktop.childCount):
            try:
                child = desktop.getChildAtIndex(i)
                print(f"App {i}: '{child.name}' (Role: {child.getRoleName()})")
            except: pass
        print("----------------------------")

    finally:
        proc.terminate()

if __name__ == "__main__":
    debug_calc_name()
