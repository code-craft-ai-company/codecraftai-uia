
try:
    import pyatspi
    print("pyatspi imported")
    try:
        print(f"KEY_SYM: {pyatspi.KEY_SYM}")
        print(f"KEY_STRING: {pyatspi.KEY_STRING}")
        print(f"KEY_PRESS: {pyatspi.KEY_PRESS}")
        print(f"KEY_RELEASE: {pyatspi.KEY_RELEASE}")
        print(f"KEY_PRESSRELEASE: {pyatspi.KEY_PRESSRELEASE}")
    except AttributeError as e:
        print(f"Attribute error: {e}")
        
    print(f"dir(pyatspi): {dir(pyatspi)}")

except ImportError:
    print("pyatspi not found")
