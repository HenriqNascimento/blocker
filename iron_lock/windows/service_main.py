import time
import sys
import os
import shutil
import requests
import socket
import logging
from pathlib import Path
import locker

# Constants
HOSTS_PATH = os.path.join(os.environ["SystemRoot"], "System32", "drivers", "etc", "hosts")
BACKUP_PATH = os.path.join(locker.LOCK_FILE_DIR, "hosts.backup")
BLOCKLIST_URL = "https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn/hosts"
# For testing/dev, we might use a smaller list or local file
REFRESH_INTERVAL = 30 # Check every 30 seconds

logging.basicConfig(
    filename=os.path.join(locker.LOCK_FILE_DIR, "service.log"),
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def backup_hosts():
    if not os.path.exists(BACKUP_PATH):
        if os.path.exists(HOSTS_PATH):
            shutil.copy(HOSTS_PATH, BACKUP_PATH)
            logging.info("Hosts file backed up.")

def update_blocklist():
    """Downloads and applies the blocklist"""
    try:
        logging.info("Downloading blocklist...")
        response = requests.get(BLOCKLIST_URL, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Basic validation to ensure it looks like a hosts file
            if "127.0.0.1" in content or "0.0.0.0" in content:
                # We need to preserve user's original localhost entries if possible
                # For this "Total Lock" version, we might just overwrite to be safe, 
                # but let's be polite and prepend standard localhost
                
                header = "# IronLock Enforcement Active\n127.0.0.1 localhost\n::1 localhost\n\n"
                
                with open(HOSTS_PATH, 'w', encoding='utf-8') as f:
                    f.write(header + content)
                
                logging.info("Hosts file updated successfully.")
                return True
    except Exception as e:
        logging.error(f"Failed to update blocklist: {e}")
    return False

def enforce_lock():
    """Checks lock status and ensures hosts file is compliant"""
    status = locker.get_lock_status()
    
    if status["status"] == "locked":
        # Check if hosts file is modified (simplified check by size or content)
        # For now, we simply re-apply if we suspect it's wrong, 
        # but to save IO, we rely on the update_blocklist logic mostly.
        # A real watchdog would hash the file.
        
        # Ensure we are blocking
        # If the file is too small (e.g. user deleted it), restore/redownload
        if os.path.exists(HOSTS_PATH):
            size = os.path.getsize(HOSTS_PATH)
            if size < 1000: # Suspiciously small
                logging.warning("Hosts file too small, restoring...")
                update_blocklist()
        else:
             logging.warning("Hosts file missing, restoring...")
             update_blocklist()
             
    elif status["status"] == "eligible_for_unlock":
        # We don't auto-unlock; user must explicitly request it via UI tool
        pass

def main_loop():
    backup_hosts()
    locker.ensure_dir()
    
    # Initial Setup
    if locker.get_lock_status()["status"] != "locked":
        # If not locked, we assume this is first run or unlocked state.
        pass

    logging.info("IronLock Service Started")
    
    # Try initial blocklist download
    update_blocklist()

    while True:
        try:
            enforce_lock()
            enforce_browser_policies()
        except Exception as e:
            logging.error(f"Loop error: {e}")
        
        time.sleep(REFRESH_INTERVAL)

def enforce_browser_policies():
    """
    Enforces 'Cloudflare Family' DNS-over-HTTPS in Chrome and Edge via Registry.
    This bypasses local DNS settings and forces the browser to use a filtering resolver.
    """
    import winreg
    
    POLICIES = [
        (r"SOFTWARE\Policies\Google\Chrome", "DnsOverHttpsMode", "secure"),
        (r"SOFTWARE\Policies\Google\Chrome", "DnsOverHttpsTemplates", "https://family.cloudflare-dns.com/dns-query"),
        (r"SOFTWARE\Policies\Microsoft\Edge", "DnsOverHttpsMode", "secure"),
        (r"SOFTWARE\Policies\Microsoft\Edge", "DnsOverHttpsTemplates", "https://family.cloudflare-dns.com/dns-query"),
    ]
    
    for path, name, value in POLICIES:
        try:
            # Create Key if not exists
            try:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path)
            except OSError:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path)
            
            # Set Value
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
        except Exception as e:
            logging.error(f"Reg Error {path}: {e}")

    # Force Flushing DNS to clear any cached bad IPs
    try:
        if os.name == 'nt':
             subprocess.run("ipconfig /flushdns", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

if __name__ == "__main__":
    if not is_admin():
        print("Error: Must run as Administrator")
        sys.exit(1)
        
    try:
        main_loop()
    except KeyboardInterrupt:
        pass
