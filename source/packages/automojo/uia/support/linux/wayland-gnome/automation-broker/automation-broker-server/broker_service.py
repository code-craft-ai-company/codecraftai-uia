#!/usr/bin/env python3
import os
import sys
import shutil
import base64
import subprocess
import argparse
import pathlib

EXTENSION_UUID = "com.automojo.automationbroker@automojo"
TOKEN_FILE = "automation-broker.token"
SOCK_FILE = "automation-broker.sock"

def get_xdg_runtime_dir():
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if not runtime_dir:
        print("Error: XDG_RUNTIME_DIR is not set.")
        sys.exit(1)
    return pathlib.Path(runtime_dir)

def get_extension_src_path():
    # Assuming this script is in .../automation-broker-server/broker_service.py
    # and extension is in .../automation-broker-ext/
    script_dir = pathlib.Path(__file__).parent.absolute()
    ext_dir = script_dir.parent / "automation-broker-ext"
    return ext_dir

def get_extension_install_path():
    data_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return pathlib.Path(data_dir) / "gnome-shell" / "extensions" / EXTENSION_UUID

def install():
    src = get_extension_src_path()
    dest = get_extension_install_path()

    if not src.exists():
        print(f"Error: Source directory not found at {src}")
        sys.exit(1)

    print(f"Installing extension from {src} to {dest}...")

    if dest.exists():
        if dest.is_symlink():
            print(f"Removing existing symlink at {dest}")
            dest.unlink()
        elif dest.is_dir():
            print(f"Removing existing directory at {dest}")
            shutil.rmtree(dest)
        else:
            print(f"Removing existing file at {dest}")
            dest.unlink()

     # Create parent dir if needed
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Symlink for development convenience, or copy?
    # Symlink is better for dev.
    os.symlink(src, dest)
    print(f"Extension installed. You may need to restart GNOME Shell (Alt+F2, r) or log out/in.")
    
    # Try to enable it, though it might fail if shell hasn't picked it up yet
    try:
        subprocess.run(["gnome-extensions", "enable", EXTENSION_UUID], check=False)
    except Exception as e:
        print(f"Warning: Could not enable extension immediately: {e}")

def start():
    runtime_dir = get_xdg_runtime_dir()
    token_path = runtime_dir / TOKEN_FILE

    # Generate token
    token = base64.b64encode(os.urandom(24)).decode("utf-8")
    
    # Write token with restricted permissions
    # umask to ensure 0600 (rw-------)
    old_umask = os.umask(0o177)
    try:
        with open(token_path, "w") as f:
            f.write(token)
    finally:
        os.umask(old_umask)
    
    print(f"Token written to {token_path}")

    # Enable extension
    print("Enabling GNOME extension...")
    try:
        subprocess.run(["gnome-extensions", "enable", EXTENSION_UUID], check=True)
        print("Extension enabled. Broker should be running.")
    except subprocess.CalledProcessError:
        print("Error: Failed to enable extension. Is it installed?")
        sys.exit(1)

def stop():
    runtime_dir = get_xdg_runtime_dir()
    token_path = runtime_dir / TOKEN_FILE
    sock_path = runtime_dir / SOCK_FILE

    # Disable extension
    print("Disabling GNOME extension...")
    subprocess.run(["gnome-extensions", "disable", EXTENSION_UUID], check=False)

    # Remove artifacts
    if token_path.exists():
        token_path.unlink()
        print(f"Removed {token_path}")
    
    if sock_path.exists():
        sock_path.unlink()
        print(f"Removed {sock_path}")

def uninstall():
    dest = get_extension_install_path()
    
    # Stop the service first
    stop()

    if dest.exists():
        if dest.is_symlink():
            print(f"Removing symlink at {dest}")
            dest.unlink()
        elif dest.is_dir():
            print(f"Removing directory at {dest}")
            shutil.rmtree(dest)
        else:
            print(f"Removing file at {dest}")
            dest.unlink()
        print("Extension uninstalled.")
    else:
        print(f"Extension not found at {dest}")

def status():
    runtime_dir = get_xdg_runtime_dir()
    token_path = runtime_dir / TOKEN_FILE
    sock_path = runtime_dir / SOCK_FILE
    
    # Check extension status
    ext_state = "unknown"
    try:
        proc = subprocess.run(["gnome-extensions", "info", EXTENSION_UUID], capture_output=True, text=True)
        if "State: ENABLED" in proc.stdout:
            ext_state = "ENABLED"
        elif "State: DISABLED" in proc.stdout:
            ext_state = "DISABLED"
        else:
             # Fallback parsing or just assume based on output presence
             if proc.returncode == 0:
                 ext_state = "INSTALLED (State unknown)"
             else:
                 ext_state = "NOT INSTALLED"
    except FileNotFoundError:
        ext_state = "command not found"

    print(f"Extension Status: {ext_state}")
    print(f"Token File: {'Present' if token_path.exists() else 'Missing'}")
    print(f"Socket File: {'Present' if sock_path.exists() else 'Missing'}")

def main():
    parser = argparse.ArgumentParser(description="Manage Automation Broker Service")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("install", help="Install the GNOME extension")
    subparsers.add_parser("uninstall", help="Uninstall the GNOME extension")
    subparsers.add_parser("start", help="Start the broker service (enable ext + token)")
    subparsers.add_parser("stop", help="Stop the broker service")
    subparsers.add_parser("status", help="Check status")

    args = parser.parse_args()

    if args.command == "install":
        install()
    elif args.command == "uninstall":
        uninstall()
    elif args.command == "start":
        start()
    elif args.command == "stop":
        stop()
    elif args.command == "status":
        status()

if __name__ == "__main__":
    main()
