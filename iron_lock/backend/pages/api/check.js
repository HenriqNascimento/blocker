import CryptoJS from 'crypto-js';
import sgMail from '@sendgrid/mail';

// Initialize SendGrid (Optional here, reused for backup email if needed)
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const APP_SECRET = process.env.APP_SECRET || 'fallback-secret-dont-use-in-prod';
const FROM_EMAIL = process.env.FROM_EMAIL || 'noreply@yourdomain.com';

export default async function handler(req, res) {
    const { token } = req.query;

    if (!token) {
        return res.status(400).send("No token provided.");
    }

    try {
        // 1. Decrypt
        // Revert URL encoding handled by Next.js mostly, but be careful
        const bytes = CryptoJS.AES.decrypt(token, APP_SECRET);
        const decryptedData = bytes.toString(CryptoJS.enc.Utf8);

        if (!decryptedData) {
            throw new Error("Invalid Token");
        }

        const data = JSON.parse(decryptedData);
        const { k: key, t: unlockTime, e: email } = data;
        const now = Date.now();

        // 2. Check Time
        if (now < unlockTime) {
            // LOCKED
            const remaining = unlockTime - now;
            const days = Math.floor(remaining / (1000 * 60 * 60 * 24));
            const hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

            return res.send(`
                <html>
                    <body style="background: #111; color: #eee; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh;">
                        <h1 style="font-size: 3rem;">LOCKED</h1>
                        <p style="font-size: 1.5rem;">Access Denied.</p>
                        <div style="background: #333; padding: 20px; border-radius: 10px; margin-top: 20px;">
                            Time Remaining: <strong>${days} Days, ${hours} Hours</strong>
                        </div>
                        <p style="margin-top: 50px; color: #666;">Come back later.</p>
                    </body>
                </html>
            `);
        } else {
            // UNLOCKED

            // Optional: Resend backup email with key just in case user closes tab
            // const msg = { ... }
            // await sgMail.send(msg);

            return res.send(`
                <html>
                    <body style="background: #0f0; color: #000; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh;">
                        <h1 style="font-size: 3rem;">UNLOCKED</h1>
                        <p style="font-size: 1.5rem;">You have successfully waited 30 days.</p>
                        
                        <div style="background: #fff; padding: 30px; border-radius: 10px; margin-top: 20px; border: 4px solid #000;">
                            <p style="margin: 0; font-size: 0.9rem; color: #666;">YOUR UNLOCK KEY:</p>
                            <h2 style="margin: 10px 0; font-size: 2.5rem; letter-spacing: 2px;">${key}</h2>
                        </div>
                        
                        <p style="margin-top: 30px;">
                            Run <b>CHECK_STATUS_WINDOWS.bat</b> and enter this key.
                        </p>
                    </body>
                </html>
            `);
        }

    } catch (e) {
        return res.status(400).send("Invalid or Corrupted Token. " + e.message);
    }
}
