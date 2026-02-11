import os
import json
import time
import hashlib
import hmac
import datetime
import secrets
import string
from pathlib import Path

# Configuration
APP_NAME = "IronLock"
LOCK_FILE_DIR = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), APP_NAME)
LOCK_FILE_PATH = os.path.join(LOCK_FILE_DIR, "lock.json")
SECRET_KEY = b"IRON_LOCK_SELF_CONTROL_KEY_2025" 
LOCK_DURATION_DAYS = 30

def ensure_dir():
    if not os.path.exists(LOCK_FILE_DIR):
        os.makedirs(LOCK_FILE_DIR)

def sign_data(data_str):
    return hmac.new(SECRET_KEY, data_str.encode('utf-8'), hashlib.sha256).hexdigest()

def hash_master_key(key):
    return hashlib.sha256(key.encode('utf-8')).hexdigest()

def save_lock_status(email, key_hash):
    """Saves the lock status with Key Hash only (Key itself is discarded)"""
    ensure_dir()
    now = datetime.datetime.now()
    unlock_date = now + datetime.timedelta(days=LOCK_DURATION_DAYS)
    
    data = {
        "start_timestamp": now.timestamp(),
        "unlock_timestamp": unlock_date.timestamp(),
        "start_date_human": str(now),
        "unlock_date_human": str(unlock_date),
        "user_email": email,
        "key_hash": key_hash,
        "mode": "cloud_verified"
    }
    
    data_str = json.dumps(data, sort_keys=True)
    signature = sign_data(data_str)
    
    final_record = {
        "data": data,
        "signature": signature
    }
    
    with open(LOCK_FILE_PATH, 'w') as f:
        json.dump(final_record, f, indent=4)
    
    return True

def get_lock_status():
    if not os.path.exists(LOCK_FILE_PATH):
        return {"status": "unlocked", "message": "No lock active."}
    
    try:
        with open(LOCK_FILE_PATH, 'r') as f:
            record = json.load(f)
        
        data = record.get("data")
        stored_signature = record.get("signature")
        
        data_str = json.dumps(data, sort_keys=True)
        expected_signature = sign_data(data_str)
        
        if not hmac.compare_digest(stored_signature, expected_signature):
            return {"status": "tampered", "message": "Lock file integrity check failed!"}
        
        unlock_ts = data["unlock_timestamp"]
        current_ts = time.time()
        remaining_seconds = unlock_ts - current_ts
        
        if remaining_seconds <= 0:
            return {"status": "eligible_for_unlock", "message": "Time lock expired."}
        else:
            days = int(remaining_seconds // 86400)
            hours = int((remaining_seconds % 86400) // 3600)
            return {
                "status": "locked", 
                "message": f"Locked. Remaining: {days} days, {hours} hours.",
                "remaining_seconds": remaining_seconds
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def verify_key(input_key):
    try:
        with open(LOCK_FILE_PATH, 'r') as f:
            record = json.load(f)
        
        saved_hash = record["data"].get("key_hash")
        if not saved_hash:
            return False
            
        input_hash = hash_master_key(input_key.strip())
        return input_hash == saved_hash
    except:
        return False

def unlock_system():
    """Reverses the hardening measures. Requires Admin."""
    try:
        APP_NAME = "IronLock"
        INSTALL_DIR = r"C:\Program Files\IronLock"
        
        # 1. Remove Scheduled Task
        os.system(f'schtasks /Delete /TN "{APP_NAME}\\IronLockCore" /F')
        
        # 2. Restore Permissions using SID *S-1-1-0 (Everyone)
        os.system(f'icacls "{INSTALL_DIR}" /reset /t /c')
        os.system(f'icacls "{INSTALL_DIR}" /grant *S-1-1-0:F /t /c')
        
        print("System unlocked. You can now delete the folder.")
        return True
    except Exception as e:
        print(f"Unlock failed: {e}")
        return False

if __name__ == "__main__":
    status = get_lock_status()
    print(f"Current Status: {status}")
    
    if status["status"] == "eligible_for_unlock":
        print("\n" + "="*40)
        print("TIME LOCK EXPIRED")
        print("Please enter the Key received via Email.")
        print("="*40 + "\n")
        
        key = input("Unlock Key: ")
        
        if verify_key(key):
            print("KEY VERIFIED.")
            confirm = input("Unlock System? (yes/no): ")
            if confirm.lower() == "yes":
                unlock_system()
        else:
            print("INVALID KEY.")
    elif status["status"] == "locked":
        print("Come back later.")
