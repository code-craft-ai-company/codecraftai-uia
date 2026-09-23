
import pyatspi

def dump(obj, indent=""):
    try:
        print(f"{indent}{obj.name} (Role: {obj.getRoleName()})")
        if obj.childCount > 0:
            for i in range(obj.childCount):
                try:
                    dump(obj.getChildAtIndex(i), indent + "  ")
                except Exception:
                    # Best-effort dump; a child that disappears or cannot be queried is skipped.
                    pass
    except Exception:
        # Best-effort dump; accessible objects that go defunct while walking the tree are skipped.
        pass

if __name__ == "__main__":
    reg = pyatspi.Registry
    desktop = reg.getDesktop(0)
    print("Dumping AT-SPI Desktop (0)...")
    dump(desktop)
