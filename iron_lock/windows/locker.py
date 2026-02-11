import os
import json
import time
import hashlib
import hmac
import datetime
import secrets
import string
import base64
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

def generate_master_key():
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(20))

def simple_encrypt(key, secret):
    # Basic XOR obfuscation sufficient for "Self-Control" against non-technical users
    # Real encryption would use AES, but dependency management (pycryptodome) is hard here.
    # XOR + Base64
    repeated_secret = (secret * (len(key) // len(secret) + 1))[:len(key)]
    xor_bytes = bytes(a ^ b for a, b in zip(key.encode(), repeated_secret))
    return base64.b64encode(xor_bytes).decode()

def simple_decrypt(enc_str, secret):
    enc_bytes = base64.b64decode(enc_str)
    repeated_secret = (secret * (len(enc_bytes) // len(secret) + 1))[:len(enc_bytes)]
    xor_bytes = bytes(a ^ b for a, b in zip(enc_bytes, repeated_secret))
    return xor_bytes.decode()

def create_lock(user_email="unknown"):
    ensure_dir()
    now = datetime.datetime.now()
    unlock_date = now + datetime.timedelta(days=LOCK_DURATION_DAYS)
    
    # Generate Key strictly for internal storage
    master_key = generate_master_key()
    
    # Encrypt Key using our app secret (so user can't read it easily from JSON)
    encrypted_key = simple_encrypt(master_key, SECRET_KEY)
    
    data = {
        "start_timestamp": now.timestamp(),
        "unlock_timestamp": unlock_date.timestamp(),
        "start_date_human": str(now),
        "unlock_date_human": str(unlock_date),
        "user_email": user_email,
        "encrypted_key": encrypted_key 
    }
    
    data_str = json.dumps(data, sort_keys=True)
    signature = sign_data(data_str)
    
    final_record = {
        "data": data,
        "signature": signature
    }
    
    with open(LOCK_FILE_PATH, 'w') as f:
        json.dump(final_record, f, indent=4)
    
    # Return nothing. Key is hidden.
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

def reveal_key():
    status = get_lock_status()
    if status["status"] != "eligible_for_unlock":
        return None
        
    try:
        with open(LOCK_FILE_PATH, 'r') as f:
            record = json.load(f)
        enc_key = record["data"]["encrypted_key"]
        return simple_decrypt(enc_key, SECRET_KEY)
    except:
        return None

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
    # Test block
    status = get_lock_status()
    print(f"Current Status: {status}")
    
    if status["status"] == "eligible_for_unlock":
        key = reveal_key()
        if key:
            print("\n" + "="*40)
            print("TIME CAPSULE UNLOCKED")
            print(f"KEY: {key}")
            print("="*40 + "\n")
            
            confirm = input("Generate Unlock Token? (yes/no): ")
            if confirm.lower() == "yes":
                unlock_system()
        else:
            print("Error retrieving key.")
    elif status["status"] == "locked":
        print("Come back later.")
