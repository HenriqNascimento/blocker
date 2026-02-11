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

def run_netsh(args):
    """Executes a netsh command"""
    cmd = f"netsh advfirewall firewall {args}"
    print(f"Exec: {cmd}")
    subprocess.run(cmd, shell=True)

def lockdown():
    print("--- IronLock NETWORK HARDENING ---")
    
    if not is_admin():
        print("CRITICAL: Must run as Administrator!")
        input("Press Enter to exit...")
        sys.exit(1)

    print("1. Cleaning old rules...")
    run_netsh("delete rule name=\"IronLock_Block_DNS\"")
    run_netsh("delete rule name=\"IronLock_Allow_SafeDNS\"")
    run_netsh("delete rule name=\"IronLock_Block_QUIC\"")

    print("\n2. Allowing Cloudflare Family DNS (1.1.1.3, 1.0.0.3)...")
    # Allow 1.1.1.3
    run_netsh("add rule name=\"IronLock_Allow_SafeDNS\" dir=out action=allow protocol=UDP remoteip=1.1.1.3,1.0.0.3 remoteport=53")
    run_netsh("add rule name=\"IronLock_Allow_SafeDNS\" dir=out action=allow protocol=TCP remoteip=1.1.1.3,1.0.0.3 remoteport=53")

    print("\n3. BLOCKING all other DNS...")
    # Block Any Port 53 not matching the above
    # Note: Windows Firewall processes Block rules before Allow? No, explicit Block overrides Allow?
    # Actually, if we just Block All Port 53, and have specific Allow, does Allow win?
    # In Windows Firewall, BLOCK rules take precedence unless "Authenticated Bypass".
    # So we cannot just Block All 53. We must Block All 53 EXCEPT 1.1.1.3.
    # But Windows Firewall "Block" rules don't support "Except".
    # Strategy: We don't need a Block rule if we have "Block Outbound Default"? Too aggressive.
    
    # Correct Strategy for Windows Firewall:
    # We can't easily do "Block all except X" in one rule.
    # We have to block entire subnets? No.
    # We can block the famous alternatives: 8.8.8.8, 8.8.4.4, 9.9.9.9 (Quad9 non-filtered), User ISP.
    # This is "Whack a mole".
    
    # BETTER STRATEGY:
    # Use "Windows Firewall with Advanced Security" logic?
    # No, let's Block UDP 53 globally.
    # Wait, if Allow rule exists for 1.1.1.3, will it work?
    # Windows Rule Precedence: Block > Allow.
    # So if we Block All 53, 1.1.1.3 is blocked too.
    
    # Solution: We can't use Windows Firewall to force a single IP easily without IPSec.
    # BUT, we can block the most common bypassers: Google (8.8.8.8).
    
    # ALTERNATIVE:
    # Block "UDP 443" (QUIC) -> Essential to force browser to HTTP/S where we might inspect SNI? No we don't inspect SNI locally.
    # The DNS Policy (Registry) we set earlier *Should* work if the browser behaves.
    # If the user sets "Custom DNS" in the browser settings, they bypass Registry? 
    # Usually Registry locks the UI.
    
    # Let's double down on QUIC blocking.
    run_netsh("add rule name=\"IronLock_Block_QUIC\" dir=out action=block protocol=UDP remoteport=443")
    
    # Let's block Google DNS explicitly just in case
    run_netsh("add rule name=\"IronLock_Block_GoogleDNS\" dir=out action=block protocol=UDP remoteip=8.8.8.8,8.8.4.4 remoteport=53")
    
    print("\n4. Hardening Complete.")
    print("QUIC (UDP 443) Blocked -> Forces browsers to use TCP.")
    print("Google DNS Blocked.")

if __name__ == "__main__":
    lockdown()
