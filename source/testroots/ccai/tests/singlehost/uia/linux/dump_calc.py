import pyatspi
import time
import os

def dump(el, indent=""):
    try:
        print(f"{indent}{el.get_role_name()}: '{el.name}'")
        if el.childCount > 0:
            for i in range(el.childCount):
                dump(el.getChildAtIndex(i), indent + "  ")
    except Exception:
        # Best-effort dump; accessible objects that go defunct while walking the tree are skipped.
        pass

def main():
    registry = pyatspi.Registry
    desktop = registry.getDesktop(0)
    
    # Launch calc
    import subprocess
    env = os.environ.copy()
    env['GDK_BACKEND'] = 'x11'
    p = subprocess.Popen(["gnome-calculator"], env=env)
    time.sleep(2)
    
    calc = None
    for app in desktop:
        if app.name == "gnome-calculator":
            calc = app
            break
            
    if calc:
        print("Found Calculator. Dumping tree:")
        dump(calc)
    else:
        print("Calculator not found.")
        
    p.terminate()

if __name__ == "__main__":
    main()
