
import os
import struct
import time
import fcntl

# Constants
EV_SYN = 0x00
EV_KEY = 0x01
EV_ABS = 0x03

ABS_X = 0x00
ABS_Y = 0x01

BTN_LEFT = 0x110
BTN_RIGHT = 0x111
BTN_TOUCH = 0x14a # Sometimes needed for tablets

SYN_REPORT = 0

UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_SET_ABSBIT = 0x40045567
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502
UI_DEV_SETUP = 0x405c5503

def emit(fd, type, code, value):
    timestamp = time.time()
    sec = int(timestamp)
    usec = int((timestamp - sec) * 1000000)
    event = struct.pack('llHHi', sec, usec, type, code, value)
    os.write(fd, event)

def debug_mouse_uinput_abs():
    print("Opening /dev/uinput...")
    try:
        fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
    except Exception as e:
        print(f"Error opening uinput: {e}")
        return

    try:
        print("Configuring EV_ABS (Absolute)...")
        fcntl.ioctl(fd, UI_SET_EVBIT, EV_KEY)
        fcntl.ioctl(fd, UI_SET_KEYBIT, BTN_LEFT)
        fcntl.ioctl(fd, UI_SET_KEYBIT, BTN_RIGHT)
        fcntl.ioctl(fd, UI_SET_KEYBIT, BTN_TOUCH)
        
        fcntl.ioctl(fd, UI_SET_EVBIT, EV_ABS)
        fcntl.ioctl(fd, UI_SET_ABSBIT, ABS_X)
        fcntl.ioctl(fd, UI_SET_ABSBIT, ABS_Y)
        
        # UI_DEV_SETUP for Absolute Device
        # We need to specify min/max for ABS axes in the uinput_setup/uinput_abs_setup logic...
        # Wait, UI_DEV_SETUP (struct uinput_setup) only does name/id/ff.
        # For ABS, we typically need `UI_ABS_SETUP` (0x401c5504) for newer kernels
        # OR use the legacy `uinput_user_dev` write which enables setting absmin/absmax.
        
        # Let's try legacy write first as it allows setting abs params via the struct easily? 
        # No, legacy write failed with EINVAL earlier.
        # We must use UI_ABS_SETUP if we use UI_DEV_SETUP.
        
        # struct uinput_abs_setup { __u16 code; struct input_absinfo absinfo; };
        # struct input_absinfo { __s32 value; __s32 minimum; __s32 maximum; __s32 fuzz; __s32 flat; __s32 resolution; };
        # size = 2 + (4*6) = 2 + 24 = 26 (+ padded to 4 bytes align? usually struct is packed)
        # Actually Linux structs usually align.
        
        UI_ABS_SETUP = 0x401c5504
        
        # Define screen resolution (virtual) - e.g. 1920x1080
        # This maps 0-1920 to screen width.
        MAX_X = 1920
        MAX_Y = 1080
        
        def configure_abs(axis_code, maximum):
            # input_absinfo: val, min, max, fuzz, flat, res
            absinfo = struct.pack('iiiiii', 0, 0, maximum, 0, 0, 0)
            payload = struct.pack('H', axis_code) + absinfo
            # Pad to 28 bytes? or just send?
            # It seems size is 2 (code) + 2 (pad) + 24 (absinfo) = 28 bytes typically?
            
            # Let's try packing strictly
            # struct uinput_abs_setup
            # __u16 code
            # __u16 padding (implicit?)
            # struct input_absinfo ...
            
            # Actually, we can try to rely on OS defaults but usually for ABS we MUST set max.
            fcntl.ioctl(fd, UI_ABS_SETUP, payload)

        print("Setting up ABS_X/ABS_Y via UI_ABS_SETUP...")
        try:
            configure_abs(ABS_X, MAX_X)
            configure_abs(ABS_Y, MAX_Y)
        except OSError:
            print("UI_ABS_SETUP failed. Trying legacy write approach (carefully packed)...")
            # If UI_ABS_SETUP fails, we might be stuck or need legacy struct correct packing.

        # Setup Device ID/Name
        BUS_USB = 0x03
        input_id = struct.pack('HHHH', BUS_USB, 0x1, 0x1, 1)
        name = b"CodeCraftAI Virtual Tablet"
        name_pad = name + b'\0' * (80 - len(name))
        ff_effects_max = struct.pack('I', 0)
        setup_payload = input_id + name_pad + ff_effects_max
        
        print("Calling UI_DEV_SETUP...")
        fcntl.ioctl(fd, UI_DEV_SETUP, setup_payload)
        
        print("Creating device...")
        fcntl.ioctl(fd, UI_DEV_CREATE)
        time.sleep(1.0)
        
        print("Device created. Moving to top-left (0,0)...")
        emit(fd, EV_ABS, ABS_X, 0)
        emit(fd, EV_ABS, ABS_Y, 0)
        emit(fd, EV_SYN, SYN_REPORT, 0)
        time.sleep(1)
        
        print("Moving to center (960, 540)...")
        emit(fd, EV_ABS, ABS_X, 960)
        emit(fd, EV_ABS, ABS_Y, 540)
        emit(fd, EV_SYN, SYN_REPORT, 0)
        time.sleep(1)
        
        print("Moving to bottom-right (1920, 1080)...")
        emit(fd, EV_ABS, ABS_X, 1920)
        emit(fd, EV_ABS, ABS_Y, 1080)
        emit(fd, EV_SYN, SYN_REPORT, 0)
        time.sleep(1)
        
        print("Done.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        fcntl.ioctl(fd, UI_DEV_DESTROY)
        os.close(fd)

if __name__ == "__main__":
    debug_mouse_uinput_abs()
