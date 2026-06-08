
import time
import sys
import os
import evdev
from evdev import UInput, ecodes as e

def debug_mouse_uinput():
    print("Initializing UInput Mouse Device...")
    
    # Define capabilities for a mouse
    capabilities = {
        e.EV_REL: (e.REL_X, e.REL_Y),
        e.EV_KEY: (e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE),
    }

    try:
        # Create virtual device
        ui = UInput(capabilities, name='codecraftai-virtual-mouse', version=0x3)
        print(f"Device created: {ui.name}")
        
        # Give system time to register device
        time.sleep(1)
        
        print("Moving mouse RELATIVELY (uinput is relative)...")
        print("You have 3 seconds to confirm movement...")
        time.sleep(3)
        
        # Move right 100 pixels
        print("Moving Right 100...")
        ui.write(e.EV_REL, e.REL_X, 100)
        ui.write(e.EV_REL, e.REL_Y, 0)
        ui.syn()
        time.sleep(0.5)

        # Move down 100 pixels
        print("Moving Down 100...")
        ui.write(e.EV_REL, e.REL_X, 0)
        ui.write(e.EV_REL, e.REL_Y, 100)
        ui.syn()
        time.sleep(0.5)

        # Move left 100 pixels
        print("Moving Left 100...")
        ui.write(e.EV_REL, e.REL_X, -100)
        ui.write(e.EV_REL, e.REL_Y, 0)
        ui.syn()
        time.sleep(0.5)

        # Move up 100 pixels
        print("Moving Up 100...")
        ui.write(e.EV_REL, e.REL_X, 0)
        ui.write(e.EV_REL, e.REL_Y, -100)
        ui.syn()
        
        # Cleanup
        ui.close()
        print("Done.")

    except PermissionError:
        print("ERROR: Permission denied. You need to be root or in 'input' group to use uinput.")
        print("Try running with sudo.")
    except Exception as ex:
        print(f"ERROR: {ex}")

if __name__ == "__main__":
    debug_mouse_uinput()
