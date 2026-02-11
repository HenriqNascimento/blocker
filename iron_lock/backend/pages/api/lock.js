import sgMail from '@sendgrid/mail';
import CryptoJS from 'crypto-js';

// Initialize SendGrid
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const APP_SECRET = process.env.APP_SECRET || 'fallback-secret-dont-use-in-prod';
const FROM_EMAIL = process.env.FROM_EMAIL || 'henriquenascimentoh@gmail.com';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

    const { email, key } = req.body;

    if (!email) {
        return res.status(400).json({ message: 'Email required' });
    }

    // 1. Prepare Data
    const now = Date.now();
    const unlockTime = now + (30 * 24 * 60 * 60 * 1000); // 30 Days
    // const unlockTime = now + (60 * 1000); // DEBUG: 1 Minute Unlock for testing

    // The key is either provided by client or we generate one
    const unlockKey = key || Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

    // 2. Encrypt Data (Stateless Token)
    const payload = JSON.stringify({
        k: unlockKey,      // Key
        t: unlockTime,     // Target Timestamp
        e: email           // Email (for verification/display)
    });

    // Encrypt payload using AES with APP_SECRET
    const token = CryptoJS.AES.encrypt(payload, APP_SECRET).toString();

    // URL Safe encoding (replace + with -, / with _, remove =)
    const safeToken = encodeURIComponent(token);

    // 3. Build Email
    const baseUrl = `https://${req.headers.host}`;
    const unlockLink = `${baseUrl}/api/check?token=${safeToken}`;

    const msg = {
        to: email,
        from: FROM_EMAIL, // Must be verified in SendGrid
        subject: 'IronLock Activated - 30 Day Commitment',
        text: `You have activated IronLock.\n\nTo retrieve your unlock key, wait 30 days and click here:\n${unlockLink}\n\nStrictly committed to your focus.`,
        html: `
        <div style="font-family: sans-serif; padding: 20px; text-align: center;">
            <h1>IronLock Active</h1>
            <p>You have committed to 30 days of focus.</p>
            <p>We are holding your unlock key securely.</p>
            <br/>
            <a href="${unlockLink}" style="background: #000; color: #fff; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                View Unlock Key (Available in 30 Days)
            </a>
            <p style="margin-top: 30px; font-size: 12px; color: #666;">
                Do not lose this email. This is the only way to recover your key.
            </p>
        </div>
        `,
    };

    try {
        await sgMail.send(msg);
        res.status(200).json({ success: true, message: 'Email sent' });
    } catch (error) {
        console.error(error);
        if (error.response) {
            console.error(error.response.body);
        }
        res.status(500).json({ success: false, message: 'Error sending email', error: error.message });
    }
}
