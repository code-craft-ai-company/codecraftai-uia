
import gi
import time
import threading
import sys
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

# Add source to path so we can import automojo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'source/packages')))

from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement


class KeyReceiverApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.KeyReceiver")
        self.window = None

    def do_activate(self):
        self.window = Gtk.ApplicationWindow(application=self, title="KeyReceiver")
        self.window.set_default_size(300, 200)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window.add(box)
        
        label = Gtk.Label(label="Type here:")
        box.pack_start(label, False, False, 10)
        
        self.entry = Gtk.Entry()
        box.pack_start(self.entry, False, False, 10)
        self.entry.connect("key-release-event", self.on_key)
        
        self.status = Gtk.Label(label="Waiting...")
        box.pack_start(self.status, False, False, 10)
        
        self.window.show_all()

    def on_key(self, widget, event):
        text = self.entry.get_text()
        self.status.set_text(f"Received: {text}")
        return False

def run_automation():
    time.sleep(3.0) # Wait a bit more for app registration
    print("Automation starting...")
    
    automation = AutomationFactory.get_automation_engine()
    # Gtk.Application usually exposes itself with the title or ID
    # Let's dump available apps to debug
    import pyatspi
    reg = pyatspi.Registry
    desktop = reg.getDesktop(0)
    print(f"Desktop child count: {desktop.childCount}")
    for i in range(desktop.childCount):
        try:
            child = desktop.getChildAtIndex(i)
            print(f"App {i}: {child.name}")
        except: pass

    target_name = "verify_linux_keys_gtk.py"
    app = automation.get_application_by_name(target_name)
    if not app:
        # Fallback to KeyReceiver just in case
        app = automation.get_application_by_name("KeyReceiver") 
    
    if not app:
        print("FAIL: KeyReceiver app not found")
        # Try finding by 'KeyReceiver' or 'org.example.KeyReceiver'
        # But let's dump specific logic in debug if needed
    else:
        print(f"Found app: {app.name}")
        windows = app.get_windows()
        if not windows:
            print("FAIL: No windows found")
        else:
            main_window = windows[0]
            print(f"Found window: {main_window.name}")
            
            try:
                main_window.activate()
                time.sleep(1.0)
                
                print("Strategy 1: Find entry and type 'abc'")
                
                # Helper to find entry
                def find_entry(el, depth=0):
                    if depth > 10: return None
                    native = getattr(el, '_native_obj', el)
                    try:
                        role_name = el.role_name
                        if role_name in ["text", "entry", "text entry"]: 
                            return el
                    except: pass
                    
                    if hasattr(native, 'childCount'):
                        for i in range(native.childCount):
                            try:
                                found = find_entry(LinuxElement(native.getChildAtIndex(i)), depth+1)
                                if found: return found
                            except: pass
                    return None
                    
                entry = find_entry(main_window)
                if entry:
                    print(f"Found entry: {entry.role_name}")
                    entry.click()
                    time.sleep(0.5)
                    try:
                        entry.type_keys("abc")
                        print("Typed 'abc'")
                    except Exception as e:
                        print(f"Type keys failed: {e}")
                else:
                    print("Entry element not found via AT-SPI")
                
                time.sleep(2.0)
            except Exception as e:
                print(f"Automation failed: {e}")

    print("Automation finished.")
    # Stop the Gtk loop
    # We need a reference to the app to quit it properly?
    # Or just exit process
    os._exit(0)

if __name__ == "__main__":
    app = KeyReceiverApp()
    
    # Run automation in separate thread
    t = threading.Thread(target=run_automation)
    t.start()
    
    app.run(None)

