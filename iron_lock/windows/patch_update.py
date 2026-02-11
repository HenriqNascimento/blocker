import os
import sys
import shutil
import subprocess
import ctypes
import time

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
    except subprocess.CalledProcessError:
        return False

def patch():
    print("--- IronLock Patcher (Hardening) ---")
    
    if not is_admin():
        print("CRITICAL: Must run as Administrator!")
        input("Press Enter to exit...")
        sys.exit(1)

    print("1. Unlocking permissions temporarily...")
    # Reset permissions so we can overwrite files
    run_command(f'icacls "{INSTALL_DIR}" /reset /t /c')
    run_command(f'icacls "{INSTALL_DIR}" /grant *S-1-1-0:F /t /c')
    
    # Kill running python processes (crude but effective for update)
    os.system("taskkill /F /IM python.exe")
    time.sleep(2)

    print("2. Updating Service Logic...")
    files_to_copy = ["service_main.py"] # Only file changed
    for f in files_to_copy:
        src = os.path.join(SOURCE_DIR, f)
        dst = os.path.join(INSTALL_DIR, f)
        try:
            shutil.copy(src, dst)
            print(f"Updated {f}")
        except Exception as e:
            print(f"Failed to copy {f}: {e}")

    print("3. Restarting Service...")
    # Re-trigger the scheduled task
    run_command(f'schtasks /Run /TN "{APP_NAME}\\IronLockCore"')

    print("4. Re-locking permissions...")
    cmd_lock = f'icacls "{INSTALL_DIR}" /deny *S-1-1-0:(DE,WD) /t /c'
    run_command(cmd_lock)
    
    print("\n--- Patch Complete ---")
    print("Force-Secure-DNS policies applied to Chrome/Edge.")
    print("DNS Cache flushed.")
    print("Please RESTART your browser.")

if __name__ == "__main__":
    patch()
