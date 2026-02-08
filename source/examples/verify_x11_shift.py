import sys
import time
# Mocking sys.path to ensure we can import the agent
sys.path.append('/home/myron/repos/automojo-uia/source/packages')

from automojo.uia.platforms.linux.agents.wm.x11_agent import X11WindowManagerAgent

def test_needs_shift():
    try:
        agent = X11WindowManagerAgent()
        agent._setup_keymap()
        
        test_cases = [
            ('a', False),
            ('A', True),
            ('1', False),
            ('!', True),
            ('@', True),
            ('b', False),
            ('B', True),
            ('7', False),
            ('&', True),
            (' ', False),
            ('\n', False),
            ('.', False),
            ('>', True)
        ]
        
        failed = False
        for char, expected in test_cases:
            result = agent._needs_shift(char)
            print(f"Char: '{char}' -> Expected: {expected}, Got: {result}")
            if result != expected:
                print(f"  FAILED: {char}")
                failed = True
        
        if failed:
            sys.exit(1)
        else:
            print("All checks passed!")
            sys.exit(0)
            
    except ImportError:
        print("Skipping test: Xlib not available")
        sys.exit(0)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_needs_shift()
