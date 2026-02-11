import os
import sys
import shutil
import subprocess
import ctypes
import urllib.request
import urllib.parse
import json
import secrets
import string
import hashlib
from pathlib import Path

# Import local modules
import locker

APP_NAME = "IronLock"
INSTALL_DIR = r"C:\Program Files\IronLock"
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

# HARDCODED BACKEND
BACKEND_URL = "https://blocker-beta.vercel.app"

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

def generate_master_key():
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(32))

def send_to_cloud(email, key):
    print(f"\nContacting Cloud ({BACKEND_URL})...")
    url = f"{BACKEND_URL}/api/lock"
    data = {
        "email": email,
        "key": key
    }
    
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("SUCCESS: Cloud has secured your key.")
                return True
            else:
                print(f"FAILED: Server returned {response.status}")
                return False
    except Exception as e:
        print(f"FAILED to contact cloud: {e}")
        print("Check your internet connection or the server URL.")
        return False

def install():
    print("--- IronLock Installer (Cloud Mode) ---")
    
    if not is_admin():
        print("CRITICAL: Must run as Administrator!")
        input("Press Enter to exit...")
        sys.exit(1)

    # 1. User Input
    print(f"Backend Configured: {BACKEND_URL}")
    print("\n[STEP 1] Identification")
    email = input("Enter your Email (must match SendGrid verification): ").strip()
    if not email:
        print("Email is required.")
        return

    # 2. Generate Key & Send
    print("\n[STEP 2] Generating & Securing Key...")
    master_key = generate_master_key()
    key_hash = hashlib.sha256(master_key.encode()).hexdigest()
    
    if not send_to_cloud(email, master_key):
        print("ABORTING: Could not secure key in cloud. Installation stopped to prevent lockout.")
        input("Press Enter...")
        return

    print("Key sent! Deleting local copy...")
    master_key = None # Wipe from memory variable
    
    # 3. Installation
    print("\n[STEP 3] Installing System Services...")
    if not os.path.exists(INSTALL_DIR):
        try:
            os.makedirs(INSTALL_DIR)
        except Exception as e:
            print(f"Failed to create directory: {e}")
            return

    files_to_copy = ["service_main.py", "locker.py", "watchdog.py", "remediate_system.py", "lockdown.py"]
    for f in files_to_copy:
        src = os.path.join(SOURCE_DIR, f)
        dst = os.path.join(INSTALL_DIR, f)
        try:
            if os.path.exists(src):
                shutil.copy(src, dst)
        except:
            pass

    # 4. Save Status (Only Hash)
    locker.save_lock_status(email, key_hash)

    # 5. Service Creation
    python_path = sys.executable
    script_path = os.path.join(INSTALL_DIR, "service_main.py")
    task_name = "IronLockCore"
    
    run_command(f'schtasks /Create /TN "{APP_NAME}\\{task_name}" /TR "\'{python_path}\' \'{script_path}\'" /SC ONSTART /RL HIGHEST /RU SYSTEM /F')
    run_command(f'schtasks /Run /TN "{APP_NAME}\\{task_name}"')

    # 6. Apply Network Fixes (IPv6/Registry) immediately
    # We run the logic from remediate_system.py but we can direct call it? 
    # Better to run the subprocess since it's copied
    print("Applying Network Hardening...")
    subprocess.run([python_path, os.path.join(INSTALL_DIR, "remediate_system.py")])
    subprocess.run([python_path, os.path.join(INSTALL_DIR, "lockdown.py")])

    # 7. Persistence
    print("\n[STEP 4] Locking System Permissions...")
    run_command(f'icacls "{INSTALL_DIR}" /deny *S-1-1-0:(DE,WD) /t /c')
    
    print("\n" + "="*60)
    print("IRONLOCK INSTALLED & CLOUD SECURED")
    print("="*60)
    print(f"An email has been sent to {email}.")
    print("Check it to ensure you have the Unlock Link.")
    print("Your local system DOES NOT have the key.")
    print("="*60)

if __name__ == "__main__":
    install()
