
import pyatspi
import sys

def dump(obj, indent=""):
    try:
        print(f"{indent}{obj.name} (Role: {obj.getRoleName()})")
        if obj.childCount > 0:
            for i in range(obj.childCount):
                try:
                    dump(obj.getChildAtIndex(i), indent + "  ")
                except Exception: pass
    except Exception: pass

if __name__ == "__main__":
    reg = pyatspi.Registry
    desktop = reg.getDesktop(0)
    print("Dumping AT-SPI Desktop (0)...")
    dump(desktop)
