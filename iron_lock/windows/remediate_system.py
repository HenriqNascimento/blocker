import os
import sys
import subprocess
import ctypes
import time
import shutil

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_cmd(cmd):
    print(f"CMD: {cmd}")
    subprocess.run(cmd, shell=True)

def disable_ipv6_robust():
    print("\n[1] DISABLING IPv6 (Critical)...")
    # Powershell to disable on all active adapters
    ps_cmd = "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object { Disable-NetAdapterBinding -Name $_.Name -ComponentID ms_tcpip6 }"
    subprocess.run(["powershell", "-Command", ps_cmd])
    
    # Also specifically target "Wi-Fi" and "Ethernet" just in case
    subprocess.run(["powershell", "-Command", "Disable-NetAdapterBinding -Name 'Wi-Fi' -ComponentID ms_tcpip6"])
    subprocess.run(["powershell", "-Command", "Disable-NetAdapterBinding -Name 'Ethernet' -ComponentID ms_tcpip6"])

def force_registry_policies():
    print("\n[2] FORCING REGISTRY POLICIES (Chrome/Edge)...")
    # Chrome
    run_cmd('reg add HKLM\\SOFTWARE\\Policies\\Google\\Chrome /v DnsOverHttpsMode /t REG_SZ /d secure /f')
    run_cmd('reg add HKLM\\SOFTWARE\\Policies\\Google\\Chrome /v DnsOverHttpsTemplates /t REG_SZ /d "https://family.cloudflare-dns.com/dns-query" /f')
    
    # Edge
    run_cmd('reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v DnsOverHttpsMode /t REG_SZ /d secure /f')
    run_cmd('reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v DnsOverHttpsTemplates /t REG_SZ /d "https://family.cloudflare-dns.com/dns-query" /f')

def force_hosts_write():
    print("\n[3] REWRITING HOSTS FILE...")
    HOSTS_PATH = os.path.join(os.environ["SystemRoot"], "System32", "drivers", "etc", "hosts")
    
    # SafeSearch VIPs
    content = [
        "# IronLock Remediation",
        "127.0.0.1 localhost",
        "::1 localhost",
        "",
        "# SafeSearch VIPs (Google/Bing)",
        "216.239.38.120 www.google.com",
        "216.239.38.120 google.com",
        "204.79.197.220 www.bing.com",
        "204.79.197.220 bing.com",
        "",
        "# Basic Blocklist Fallback (Top Adult Sites)",
        "0.0.0.0 www.pornhub.com",
        "0.0.0.0 pornhub.com",
        "0.0.0.0 www.xvideos.com",
        "0.0.0.0 xvideos.com",
        "0.0.0.0 www.xnxx.com",
        "0.0.0.0 xnxx.com",
        "0.0.0.0 www.xhamster.com",
        "0.0.0.0 xhamster.com",
        # Add more if needed, but the DNS Policy is the real shield
    ]
    
    try:
        # Try to make writable just in case
        run_cmd(f'attrib -r "{HOSTS_PATH}"')
        
        with open(HOSTS_PATH, "w") as f:
            f.write("\n".join(content))
        print("Hosts file rewritten successfully.")
    except Exception as e:
        print(f"Failed to write hosts: {e}")

def restart_browsers():
    print("\n[4] FLUSHING NETWORK & RESTARTING BROWSERS...")
    run_cmd("ipconfig /flushdns")
    os.system("taskkill /F /IM chrome.exe")
    os.system("taskkill /F /IM msedge.exe")
    os.system("taskkill /F /IM firefox.exe")
    os.system("taskkill /F /IM opera.exe")

def main():
    print("--- IRONLOCK REMEDIATION ---")
    if not is_admin():
        print("CRITICAL: Must run as Administrator!")
        sys.exit(1)
        
    disable_ipv6_robust()
    force_registry_policies()
    force_hosts_write()
    restart_browsers()
    
    print("\n--- REMEDIATION COMPLETE ---")
    print("Please verify blocking now.")

if __name__ == "__main__":
    main()
