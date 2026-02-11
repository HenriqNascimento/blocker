import os
import subprocess
import logging

try:
    with open("diagnosis.txt", "w", encoding="utf-8") as f:
        f.write("--- DIAGNOSIS REPORT ---\n\n")
        
        # 1. Check Hosts File
        f.write("[1] HOSTS FILE CONTENT:\n")
        try:
            hosts_path = os.path.join(os.environ["SystemRoot"], "System32", "drivers", "etc", "hosts")
            with open(hosts_path, "r", encoding="utf-8") as h:
                f.write(h.read())
        except Exception as e:
            f.write(f"Error reading hosts: {e}\n")
        
        # 2. Check DNS / IPConfig
        f.write("\n\n[2] IPCONFIG /ALL:\n")
        try:
            res = subprocess.check_output("ipconfig /all", shell=True).decode(errors="ignore")
            f.write(res)
        except Exception as e:
             f.write(f"Error ipconfig: {e}\n")

        # 3. Check Scheduled Task
        f.write("\n\n[3] SCHEDULED TASK STATUS:\n")
        try:
            res = subprocess.check_output('schtasks /Query /TN "IronLock\\IronLockCore"', shell=True).decode(errors="ignore")
            f.write(res)
        except Exception as e:
             f.write(f"Error schtasks: {e}\n")

        # 4. Check Registry Policies
        f.write("\n\n[4] REGISTRY POLICIES (Chrome):\n")
        try:
            res = subprocess.check_output('reg query HKLM\\SOFTWARE\\Policies\\Google\\Chrome /s', shell=True).decode(errors="ignore")
            f.write(res)
        except Exception as e:
             f.write(f"Error reg query: {e}\n")

        # 5. Check Firewall Rules
        f.write("\n\n[5] FIREWALL RULES (IronLock Only):\n")
        try:
            res = subprocess.check_output('netsh advfirewall firewall show rule name=all | findstr "IronLock"', shell=True).decode(errors="ignore")
            f.write(res)
        except Exception as e:
             f.write(f"Error firewall: {e}\n")

        # 6. Check Running Processes
        f.write("\n\n[6] RUNNING PYTHON PROCESSES:\n")
        try:
            res = subprocess.check_output('tasklist /FI "IMAGENAME eq python.exe"', shell=True).decode(errors="ignore")
            f.write(res)
        except Exception as e:
             f.write(f"Error tasklist: {e}\n")

    print("Diagnosis complete. File saved to diagnosis.txt")

except Exception as e:
    print(f"Critical Error: {e}")
