# IronLock for Android

## Compilation Instructions

1. **Install Android Studio**
2. **Open Project**: Select the `iron_lock/android` directory.
3. **Sync Gradle**: Android Studio will download necessary dependencies (Core KTX, AppCompat, ConstraintLayout are standard).
4. **Build APK**: Go to `Build > Build Bundle(s) / APK(s) > Build APK(s)`.

## Installation on Device

1. Install the APK.
2. Open **IronLock**.
3. **Grant Permissions**:
    - **Device Admin**: Essential to prevent uninstall.
    - **Accessibility**: Essential to prevent "Force Stop".
    - **VPN**: Essential for traffic filtering.
4. Click **Start Unlock Timer**.

## How to Uninstall (Emergency)

1. Wait 30 Days.
2. Open App, click "Request Unlock".
3. The app will disable its Admin/Accessibility protections.
4. You can then uninstall normally.
