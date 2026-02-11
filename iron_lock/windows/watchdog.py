import time
import subprocess
import sys
import os
import logging
from pathlib import Path

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_SCRIPT = os.path.join(SCRIPT_DIR, "service_main.py")
PYTHON_EXE = sys.executable

logging.basicConfig(
    filename=os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "IronLock", "watchdog.log"),
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def is_process_running(process_name_snippet):
    # This is a crude check. In production, use psutil or check PID file.
    # For now, we rely on 'tasklist'
    try:
        output = subprocess.check_output('tasklist', shell=True).decode()
        return process_name_snippet in output
    except:
        return False

def launch_service():
    logging.info(f"Launching {SERVICE_SCRIPT}...")
    # Hide window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    subprocess.Popen(
        [PYTHON_EXE, SERVICE_SCRIPT],
        cwd=SCRIPT_DIR,
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def main():
    logging.info("Watchdog started.")
    while True:
        # We need a robust way to know if OUR SPECIFIC service is running
        # Checking just 'python.exe' is bad.
        # But 'service_main.py' might not show up in tasklist as the image name.
        # Strategy: Use a lockfile for the service process?
        
        # Simpler for prototype: Just launch it blindly? No, multiple instances.
        # Better: use `psutil` if available, but we can't assume.
        # WMI query is standard.
        
        # For this step, we will assume we need to keep the "Service" alive.
        # Ideally, we should compile to EXE so tasklist shows "ironlock_service.exe".
        pass
        
        time.sleep(10)

if __name__ == "__main__":
    # Placeholder for watchdog logic
    # In a real deployment, this would use a Mutex and monitoring
    print("Watchdog placeholder - Use Windows Service Manager (SC.EXE) for real resilience.")
