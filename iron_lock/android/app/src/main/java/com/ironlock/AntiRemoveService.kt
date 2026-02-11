package com.ironlock

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.util.Log

class AntiRemoveService : AccessibilityService() {

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.d("IronLock", "Anti-Remove Service Connected")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return

        val packageName = event.packageName?.toString() ?: return
        val className = event.className?.toString() ?: ""

        // Check if we are in Settings
        if (packageName == "com.android.settings" || packageName.contains("packageinstaller")) {
            
            // We need to scan the screen for specific dangerous keywords
            if (shouldBlockScreen(event)) {
                performGlobalAction(GLOBAL_ACTION_HOME)
                // Optionally show a Toast "Access Denied by IronLock"
            }
        }
    }

    private fun shouldBlockScreen(event: AccessibilityEvent): Boolean {
        // Retrieve root node
        val rootNode = rootInActiveWindow ?: return false
        
        // Scan for "Force stop", "Uninstall", "Clear data"
        // Note: This logic needs to be localized or robust. 
        // For prototype, we search for English strings.
        val dangerousTexts = listOf("Force stop", "Uninstall", "Deactivate", "Clear storage")
        
        // Recursive search or simple find
        for (text in dangerousTexts) {
            val list = rootNode.findAccessibilityNodeInfosByText(text)
            if (list != null && list.isNotEmpty()) {
                
                // Refinement: Check if the button is Enabled/Visible
                // And check if it targets THIS app? 
                // Hard to tell context purely from text.
                // Aggressive mode: Block ANY force stop page in settings.
                
                // If the Package Name on screen is OURS, block it.
                // But accessibility event package is 'com.android.settings'.
                // To know WHICH app page is open, we need to read the title.
                
                // For a "Self-Control" app, aggressive blocking of Settings 
                // (specifically the App Info page) is acceptable/expected.
                return true
            }
        }
        return false
    }

    override fun onInterrupt() {
        // Service interrupted
    }
}
