
import os
import struct
import time
import fcntl

# Constants from linux/input.h and linux/uinput.h
EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02

REL_X = 0x00
REL_Y = 0x01

BTN_LEFT = 0x110
BTN_RIGHT = 0x111

SYN_REPORT = 0

# IOCTL codes (architecture dependent, assuming x86_64/common linux)
# _IOW(UINPUT_IOCTL_BASE, 100, int) -> 0x40045564
UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_SET_RELBIT = 0x40045566

UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502

# Helpers
def emit(fd, type, code, value):
    # struct input_event { struct timeval time; __u16 type; __u16 code; __s32 value; };
    # timeval is 16 bytes (2 longs), type 2, code 2, value 4.
    # We can pass 0 for time, kernel updates it.
    timestamp = time.time()
    sec = int(timestamp)
    usec = int((timestamp - sec) * 1000000)
    
    # Pack: llHHi
    # l = long (8 bytes on 64 bit), H = unsigned short (2 bytes), i = int (4 bytes)
    # Total 8+8+2+2+4 = 24 bytes.
    event = struct.pack('llHHi', sec, usec, type, code, value)
    os.write(fd, event)

def debug_mouse_uinput_direct():
    print("Opening /dev/uinput...")
    try:
        fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
    except PermissionError:
        print("Permission denied. Try running with sudo.")
        return
    except FileNotFoundError:
        print("/dev/uinput not found. Is the uinput module loaded?")
        return

    try:
        # Configure device capabilities
        print("Configuring EV_KEY...")
        fcntl.ioctl(fd, UI_SET_EVBIT, EV_KEY)
        fcntl.ioctl(fd, UI_SET_KEYBIT, BTN_LEFT)
        fcntl.ioctl(fd, UI_SET_KEYBIT, BTN_RIGHT)
        
        print("Configuring EV_REL...")
        fcntl.ioctl(fd, UI_SET_EVBIT, EV_REL)
        fcntl.ioctl(fd, UI_SET_RELBIT, REL_X)
        fcntl.ioctl(fd, UI_SET_RELBIT, REL_Y)
        
        # UI_DEV_SETUP (modern ioctl)
        # _IOW('U', 3, struct uinput_setup)
        # struct uinput_setup { struct input_id id; char name[80]; __u32 ff_effects_max; };
        # size = 8 + 80 + 4 = 92
        UI_DEV_SETUP = 0x405c5503
        
        print("Packing uinput_setup (modern)...")
        BUS_USB = 0x03
        
        # input_id
        input_id = struct.pack('HHHH', BUS_USB, 0x1, 0x1, 1)
        name = b"Automojo Direct Mouse"
        name_pad = name + b'\0' * (80 - len(name))
        ff_effects_max = struct.pack('I', 0)
        
        setup_payload = input_id + name_pad + ff_effects_max
        print(f"Setup payload size: {len(setup_payload)}")
        
        try:
            print("Calling IOCTL UI_DEV_SETUP...")
            fcntl.ioctl(fd, UI_DEV_SETUP, setup_payload)
        except OSError as e:
            print(f"UI_DEV_SETUP failed ({e}). Falling back to legacy write...")
            # Fallback for older kernels?
            # Reconstruct legacy struct... (omitted for brevity, previously failed)
            raise e

        # Create Device
        print("Creating device (IOCTL UI_DEV_CREATE)...")
        fcntl.ioctl(fd, UI_DEV_CREATE)
        
        print("Device created successfully. Waiting 1s...")
        time.sleep(1.0)
        
        print("Moving mouse RELATIVELY (Direct)...")
        print("You have 3 seconds to confirm movement...")
        time.sleep(3)
        
        # Move box
        steps = [
            (100, 0),   # Right
            (0, 100),   # Down
            (-100, 0),  # Left
            (0, -100)   # Up
        ]
        
        for dx, dy in steps:
            print(f"Moving {dx}, {dy}...")
            # For smoother movement, break into chunks
            for _ in range(10):
                sx = dx // 10
                sy = dy // 10
                emit(fd, EV_REL, REL_X, sx)
                emit(fd, EV_REL, REL_Y, sy)
                emit(fd, EV_SYN, SYN_REPORT, 0)
                time.sleep(0.05)
            time.sleep(0.2)
            
        print("Done moving.")
        time.sleep(1)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Destroying device...")
        fcntl.ioctl(fd, UI_DEV_DESTROY)
        os.close(fd)

if __name__ == "__main__":
    debug_mouse_uinput_direct()
