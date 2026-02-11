package com.ironlock

import android.app.Activity
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.net.VpnService
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast

class MainActivity : Activity() {

    private lateinit var statusText: TextView
    private lateinit var actionButton: Button
    
    // Admin Component
    private lateinit var adminComponent: ComponentName

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Simple UI Layout Programmatically (to avoid creating layout XML for now)
        // Or we assume layout file exists. Let's use layout file approach.
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        actionButton = findViewById(R.id.actionButton)
        
        adminComponent = ComponentName(this, AdminReceiver::class.java)

        updateStatus()

        actionButton.setOnClickListener {
            handleAction()
        }
    }

    private fun updateStatus() {
        // Check Permissions
        val isAdmin = isAdminActive()
        val isAccessibility = isAccessibilityServiceEnabled()
        
        if (!isAdmin || !isAccessibility) {
            statusText.text = "Status: VULNERABLE\nPermissions Missing"
            actionButton.text = "Enable Permissions"
        } else {
            statusText.text = "Status: SECURE\nIronLock Active"
            actionButton.text = "Start Unlock Timer (30 Days)"
        }
    }

    private fun handleAction() {
        if (!isAdminActive()) {
            // Request Device Admin
            val intent = Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN)
            intent.putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, adminComponent)
            startActivity(intent)
            return
        }
        
        // If secure, logic to start timer...
        Toast.makeText(this, "Timer Started. Come back in 30 days.", Toast.LENGTH_LONG).show()
    }

    private fun isAdminActive(): Boolean {
        val dpm = getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        return dpm.isAdminActive(adminComponent)
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        // Logic to check accessibility
        // Simplified:
        return false // Placeholder
    }
}
