
import tkinter as tk
import time
import threading
import sys
import os

# Add source to path so we can import ccai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'source/packages')))

from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement

class KeyReceiverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyReceiver")
        self.root.geometry("300x200")
        
        self.label = tk.Label(root, text="Type here:")
        self.label.pack()
        
        self.entry = tk.Entry(root)
        self.entry.pack(pady=10)
        self.entry.focus_set()
        
        self.status = tk.Label(root, text="Waiting...", fg="blue")
        self.status.pack()
        
        self.received_text = ""
        self.entry.bind("<KeyRelease>", self.on_key)

    def on_key(self, event):
        self.received_text = self.entry.get()
        self.status.config(text=f"Received: {self.received_text}")

def run_automation():
    time.sleep(2.0)
    print("Automation starting...")
    
    automation = AutomationFactory.get_automation_engine()
    app = automation.get_application_by_name("KeyReceiver")
    
    if not app:
        print("FAIL: KeyReceiver app not found")
        return

    windows = app.get_windows()
    if not windows:
        print("FAIL: No windows found")
        return
        
    main_window = windows[0]
    print(f"Found window: {main_window.name}")
    
    # Try different strategies
    try:
        main_window.activate()
        time.sleep(1.0)
        
        # Strategy 1: Type keys via pyatspi wrapper
        print("Strategy 1: wrapper type_keys 'abc'")
        try:
            # Need to find the entry element inside
            # Just typing on window often works if focus is there
            main_window.type_keys("abc")
        except Exception as e:
            print(f"Strategy 1 failed: {e}")
            
        time.sleep(1.0)
        
        # Strategy 2: Click entry then type
        print("Strategy 2: Find entry, click, type 'def'")
        # We need a robust finder for the entry
        def find_entry(el, depth=0):
            if depth > 10: return None
            if el.role_name == "text" or el.role_name == "entry": 
                return el
            native = getattr(el, '_native_obj', el)
            if hasattr(native, 'childCount'):
                for i in range(native.childCount):
                    found = find_entry(LinuxElement(native.getChildAtIndex(i)), depth+1)
                    if found: return found
            return None
            
        entry = find_entry(main_window)
        if entry:
            entry.click()
            time.sleep(0.5)
            entry.type_keys("def")
        else:
            print("Entry element not found via AT-SPI")

        time.sleep(1.0)

    finally:
        print("Automation finished.")
        # We can close the app or let user see
        # root.quit() via automation?
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyReceiverApp(root)
    
    # Run automation in separate thread
    t = threading.Thread(target=run_automation)
    t.start()
    
    # Auto close after 10s for test purposes
    root.after(10000, root.destroy)
    
    root.mainloop()
    t.join()
