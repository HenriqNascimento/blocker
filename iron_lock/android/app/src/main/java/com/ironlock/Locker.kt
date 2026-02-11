package com.ironlock

import android.content.Context
import android.util.Log
import org.json.JSONObject
import java.io.File
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

object Locker {
    private const val FILE_NAME = "lock.json"
    private const val SECRET_KEY = "IRON_LOCK_SELF_CONTROL_KEY_2025" // Matches Python key
    private const val LOCK_DURATION_DAYS = 30L
    private const val LOCK_DURATION_MS = LOCK_DURATION_DAYS * 24 * 60 * 60 * 1000

    fun createLock(context: Context): Boolean {
        try {
            val nowStr = System.currentTimeMillis().toString()
            val unlockTime = System.currentTimeMillis() + LOCK_DURATION_MS
            val unlockStr = unlockTime.toString()
            
            val dataStr = "{\"start\":\"$nowStr\",\"unlock\":\"$unlockStr\"}"
            val signature = signData(dataStr)
            
            val json = JSONObject()
            json.put("data", dataStr)
            json.put("signature", signature)
            
            val file = File(context.filesDir, FILE_NAME)
            file.writeText(json.toString())
            return true
        } catch (e: Exception) {
            e.printStackTrace()
            return false
        }
    }

    fun getStatus(context: Context): LockStatus {
        val file = File(context.filesDir, FILE_NAME)
        if (!file.exists()) return LockStatus.Unlocked("No lock found")

        try {
            val content = file.readText()
            val json = JSONObject(content)
            val dataStr = json.getString("data")
            val storedSig = json.getString("signature")
            
            if (signData(dataStr) != storedSig) {
                return LockStatus.Tampered
            }
            
            val dataJson = JSONObject(dataStr)
            val unlockTime = dataJson.getLong("unlock")
            val now = System.currentTimeMillis()
            
            if (now >= unlockTime) {
                return LockStatus.EligibleForUnlock
            } else {
                val diff = unlockTime - now
                return LockStatus.Locked(diff)
            }
            
        } catch (e: Exception) {
            return LockStatus.Error(e.message ?: "Unknown error")
        }
    }

    private fun signData(data: String): String {
        val keySpec = SecretKeySpec(SECRET_KEY.toByteArray(StandardCharsets.UTF_8), "HmacSHA256")
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(keySpec)
        val bytes = mac.doFinal(data.toByteArray(StandardCharsets.UTF_8))
        return bytes.joinToString("") { "%02x".format(it) }
    }

    sealed class LockStatus {
        data class Unlocked(val msg: String) : LockStatus()
        object Tampered : LockStatus()
        object EligibleForUnlock : LockStatus()
        data class Locked(val remainingMs: Long) : LockStatus()
        data class Error(val err: String) : LockStatus()
    }
}
