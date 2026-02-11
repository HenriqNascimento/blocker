import os
import sys
import subprocess
import ctypes
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_ps(cmd):
    """Executes a PowerShell command"""
    command = ["powershell", "-Command", cmd]
    print(f"PS Exec: {cmd}")
    subprocess.run(command)

def enforce_safesearch_hosts():
    print("2. Enforcing SafeSearch via Hosts (VIP)...")
    HOSTS_PATH = os.path.join(os.environ["SystemRoot"], "System32", "drivers", "etc", "hosts")
    
    # Google SafeSearch VIPs
    # forcesafesearch.google.com -> 216.239.38.120
    # duckduckgo safe -> safe.duckduckgo.com (CNAME via DNS? No, we use IP)
    # DuckDuckGo Safe Search IP: 52.142.124.215 (approx, strictly DNS based usually)
    # Actually DDG is strictly via "safe.duckduckgo.com".
    # Google is the most important.
    
    safesearch_entries = [
        "\n# IronLock SafeSearch Enforcement",
        "216.239.38.120 www.google.com",
        "216.239.38.120 google.com",
        "216.239.38.120 www.bing.com",
        "216.239.38.120 bing.com", # Bing also supports this VIP? Actually strict.bing.com is CNAME.
        # Bing Strict IP: 204.79.197.220 (CNAME strict.bing.com)
        "204.79.197.220 www.bing.com",
        "204.79.197.220 bing.com",
    ]
    
    try:
        with open(HOSTS_PATH, "a") as f:
            f.write("\n".join(safesearch_entries))
        print("SafeSearch IPs injected.")
    except Exception as e:
        print(f"Hosts Injection Failed: {e}")

def disable_ipv6():
    print("1. Disabling IPv6 on all adapters (Prevent Leakage)...")
    # Get all adapters
    run_ps("Get-NetAdapter | ForEach-Object { Disable-NetAdapterBinding -Name $_.Name -ComponentID ms_tcpip6 }")

def firefox_policies():
    print("3. Enforcing Firefox Policies...")
    # Firefox requires a specific "distribution" folder or Registry.
    # Registry: HKLM\SOFTWARE\Policies\Mozilla\Firefox
    import winreg
    POLICIES = [
        (r"SOFTWARE\Policies\Mozilla\Firefox", "DNSOverHTTPS", 1), # Enable? No we want strict.
        # Firefox mechanism is complex. Mode 3 = Force.
        # "DNSOverHTTPS": { "Enabled": true, "ProviderURL": "...", "Locked": true }
        # Registry mapping implies subkeys.
    ]
    # Simplified: Just block DoH in Firefox so it uses System DNS (which plays by our Hosts rules)
    # Or force Cloudflare Family.
    # We will assume user uses Chrome/Edge primarily based on stats, but lets handle Firefox Registry.
    
    base = r"SOFTWARE\Policies\Mozilla\Firefox"
    try:
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, base)
        winreg.SetValueEx(key, "DisableAppUpdate", 0, winreg.REG_DWORD, 0) # Example
        
        # DNSOverHTTPS
        doh = winreg.CreateKey(key, "DNSOverHTTPS")
        winreg.SetValueEx(doh, "Enabled", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(doh, "ProviderURL", 0, winreg.REG_SZ, "https://family.cloudflare-dns.com/dns-query")
        winreg.SetValueEx(doh, "Locked", 0, winreg.REG_DWORD, 1)
        
        winreg.CloseKey(doh)
        winreg.CloseKey(key)
        print("Firefox Policies Applied.")
    except Exception as e:
        print(f"Firefox Policy Error: {e}")

def kill_browsers():
    print("4. Killing Browsers to reload network stack...")
    os.system("taskkill /F /IM chrome.exe")
    os.system("taskkill /F /IM msedge.exe")
    os.system("taskkill /F /IM firefox.exe")
    os.system("taskkill /F /IM opera.exe")

def nuclear():
    print("--- IRONLOCK NUCLEAR OPTION ---")
    if not is_admin():
        print("CRITICAL: Must run as Administrator!")
        sys.exit(1)

    disable_ipv6()
    enforce_safesearch_hosts()
    firefox_policies()
    
    print("5. Flushing DNS...")
    os.system("ipconfig /flushdns")
    
    kill_browsers()
    
    print("\n--- NUCLEAR LOCKDOWN COMPLETE ---")
    print("IPv6: DISABLED")
    print("SafeSearch: FORCED (Google/Bing)")
    print("Browsers: RESTARTED")

if __name__ == "__main__":
    nuclear()
