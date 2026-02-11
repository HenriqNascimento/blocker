# IronLock for Windows

## Installation

1. Open PowerShell as **Administrator**.
2. Navigate to this folder: `cd iron_lock/windows`
3. Run: `python install_windows.py`
4. Confirm the service is running.

## How it Works

- **Persistence**: 
    - Installed to `C:\Program Files\IronLock`.
    - Permissions are locked so you cannot delete files.
    - Runs as a **Scheduled Task** at SYSTEM startup (highest privilege).
    - Checks `hosts` file every 30 seconds and reverts changes.
- **Filtering**:
    - Uses `hosts` file to block domains (StevenBlack User List).
- **Time Lock**:
    - `lock.json` stores the unlock date.
    - Preventing "cheat by changing clock" is hard locally, but we sign the timestamp so you can't edit the file.

## Unlocking

1. Wait 30 Days.
2. Open PowerShell as Administrator.
3. Run: `python locker.py`
4. If time has passed, it will offer to **Unlock System**.
5. Once unlocked, it removes the permissions and scheduled task, allowing you to delete the folder.
