import os
import sys
import shutil
import subprocess
import ctypes
import webbrowser
import urllib.parse
from pathlib import Path

# Import local modules (must be in same dir)
import locker

APP_NAME = "IronLock"
INSTALL_DIR = r"C:\Program Files\IronLock"
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_command(cmd):
    print(f"Running: {cmd}")
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (Non-critical): {e}")
        return False

def install():
    print("--- IronLock Installer (Time Capsule Mode) ---")
    
    if not is_admin():
        print("CRITICAL: Must run as Administrator!")
        input("Press Enter to exit...")
        sys.exit(1)

    # 1. User Input
    print("\n[STEP 1] Configuration")
    email = input("Enter your Email (for Commitment Confirmation): ").strip()
    if not email:
        email = "self@control.com"

    print("\n[STEP 2] Installation")
    if not os.path.exists(INSTALL_DIR):
        try:
            os.makedirs(INSTALL_DIR)
        except Exception as e:
            print(f"Failed to create directory: {e}")
            return

    files_to_copy = ["service_main.py", "locker.py", "watchdog.py", "remediate_system.py", "lockdown.py"] 
    # Include all relevant scripts
    for f in files_to_copy:
        src = os.path.join(SOURCE_DIR, f)
        dst = os.path.join(INSTALL_DIR, f)
        try:
            if os.path.exists(src):
                shutil.copy(src, dst)
                print(f"Copied {f}")
        except Exception as e:
            print(f"Failed to copy {f}: {e}")

    # 3. Create Service
    python_path = sys.executable
    script_path = os.path.join(INSTALL_DIR, "service_main.py")
    task_name = "IronLockCore"
    
    cmd_task = f'schtasks /Create /TN "{APP_NAME}\\{task_name}" /TR "\'{python_path}\' \'{script_path}\'" /SC ONSTART /RL HIGHEST /RU SYSTEM /F'
    run_command(cmd_task)
    run_command(f'schtasks /Run /TN "{APP_NAME}\\{task_name}"')

    # 4. Generate Lock (Time Capsule)
    print("\n[STEP 3] Generating Time Lock...")
    locker.create_lock(email)
    
    print("\n" + "="*60)
    print("LOCK ACTIVATED. KEY IS SEALED FOR 30 DAYS.")
    print("="*60)
    
    # 5. Send Confirmation Email (Mailto)
    print("\n[STEP 4] Sending Confirmation Email...")
    subject = "IronLock Active - 30 Day Commitment"
    body = f"I have activated IronLock on {locker.APP_NAME}.\nStart Date: Today.\nUnlock Date: +30 Days.\n\nI commit to this period of self-control."
    
    mailto_link = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    
    print("Opening your Email Client... Please press SEND to confirm to yourself.")
    webbrowser.open(mailto_link)
    
    input("Press Enter after sending the email...")

    # 6. Persistence
    print("\n[STEP 5] Hardening System permissions...")
    cmd_lock = f'icacls "{INSTALL_DIR}" /deny *S-1-1-0:(DE,WD) /t /c'
    run_command(cmd_lock)
    
    print("\n--- Installation Complete ---")
    print("IronLock is running.")

if __name__ == "__main__":
    install()
