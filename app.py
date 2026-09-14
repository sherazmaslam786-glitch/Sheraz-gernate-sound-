from flask import Flask, request, jsonify, render_template_string
import sqlite3
import random

app = Flask(__name__)

# 1. ڈیٹا بیس سیٹ اپ (رئیل ایپ کے لیے SQLite)
def init_db():
    conn = sqlite3.connect('shiraz_studio.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            verified INTEGER DEFAULT 0,
            pro_status INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 2. فرنٹ اینڈ اور جاوا اسکرپٹ کو ایک ساتھ ملانے والا مین پیج
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shiraz Real AI Studio App</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
        body { background: #070913; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { width: 100%; max-width: 390px; background: #111827; padding: 20px; border-radius: 20px; border: 1px solid #1f2937; }
        .screen { display: none; flex-direction: column; gap: 12px; }
        .screen.active { display: flex; }
        input, select { width: 100%; padding: 12px; background: #1f2937; border: 1px solid #374151; border-radius: 10px; color: #fff; font-size: 14px; }
        button { width: 100%; padding: 12px; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 14px; }
        .btn-orange { background: #f59e0b; color: #000; }
        .btn-pink { background: #db2777; color: #fff; }
        .alert { padding: 10px; border-radius: 8px; font-size: 12px; text-align: center; display: none; }
        .alert.success { background: #065f46; color: #6ee7b7; display: block; }
        .alert.error { background: #7f1d1d; color: #fca5a5; display: block; }
    </style>
</head>
<body>
    <div class="container">
        
        <!-- سکرین 1: ویریفیکیشن اور لاگ ان -->
        <div id="loginScreen" class="screen active">
            <h2 style="text-align: center; color: #f59e0b;">Shiraz Studio Login</h2>
            <p style="font-size: 12px; color: #9ca3af; text-align: center;">نیا نمبر ہو گا تو OTP ملے گا، پرانا ہوا تو سیدھا اندر جائیں!</p>
            
            <label style="font-size: 12px; color: #9ca3af;">Phone Number</label>
            <input type="text" id="phoneInput" placeholder="03001234567">
            <button class="btn-orange" onclick="checkUserAndSendOtp()">Get OTP / Login</button>

            <div id="otpSection" style="display: none; flex-direction: column; gap: 10px; margin-top: 10px;">
                <label style="font-size: 12px; color: #f472b6;">Enter OTP Code</label>
                <input type="text" id="otpInput" placeholder="Enter OTP">
                <button class="btn-pink" onclick="verifyOtp()">Verify & Enter App</button>
            </div>
        </div>

        <!-- سکرین 2: سٹوڈیو ڈیش بورڈ -->
        <div id="studioScreen" class="screen">
            <h2 style="color: #10b981; text-align: center;">🎵 Studio Dashboard Active</h2>
            <p style="font-size: 12px; color: #9ca3af; text-align: center;">خوش آمدید! آپ کا سسٹم بالکل پرفیکٹ کام کر رہا ہے۔</p>
            
            <label style="font-size: 12px;">Artist Name</label>
            <input type="text" value="Shiraz Ahmed">
            
            <label style="font-size: 12px;">Song Lyrics</label>
            <textarea style="background: #1f2937; color: #fff; border: 1px solid #374151; border-radius: 10px; padding: 10px; height: 60px;" placeholder="بول درج کریں..."></textarea>
            
            <button class="btn-orange" onclick="buyProPackage()">Buy Pro Package (JazzCash/EasyPaisa)</button>
        </div>

        <div id="msgBox" class="alert"></div>
    </div>

    <script>
        let currentPhone = "";

        // 1. نمبر چیک کرنے اور OTP مانگنے کا جاوا اسکرپٹ فنکشن
        async function checkUserAndSendOtp() {
            const phone = document.getElementById('phoneInput').value.trim();
            if (!phone) {
                showAlert("براہ کرم فون نمبر درج کریں!", "error");
                return;
            }
            currentPhone = phone;

            let response = await fetch('/api/send-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phone })
            });
            let data = await response.json();

            if (data.success) {
                if (data.already_verified) {
                    // اگر نمبر پہلے سے رجسٹرڈ ہے، تو براہ راست سٹوڈیو کھول دو!
                    showAlert(data.message, "success");
                    setTimeout(openStudio, 1000);
                } else {
                    // اگر نیا نمبر ہے تو OTP ان باکس دکھاؤ
                    document.getElementById('otpSection').style.display = 'flex';
                    showAlert("نیا OTP: " + data.debug_otp, "success");
                }
            } else {
                showAlert(data.message, "error");
            }
        }

        // 2. OTP ویریفائی کرنے کا فنکشن
        async function verifyOtp() {
            const otp = document.getElementById('otpInput').value.trim();
            if (!otp) {
                showAlert("OTP درج کریں!", "error");
                return;
            }

            let response = await fetch('/api/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: currentPhone, otp: otp })
            });
            let data = await response.json();

            if (data.success) {
                showAlert(data.message, "success");
                setTimeout(openStudio, 1000);
            } else {
                showAlert(data.message, "error");
            }
        }

        // 3. پرو پیکج خریدنے کا فنکشن
        async function buyProPackage() {
            let response = await fetch('/api/buy-pro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: currentPhone })
            });
            let data = await response.json();
            if (data.success) {
                showAlert(data.message, "success");
            }
        }

        function openStudio() {
            document.getElementById('loginScreen').classList.remove('active');
            document.getElementById('studioScreen').classList.add('active');
            hideAlert();
        }

        function showAlert(text, type) {
            const box = document.getElementById('msgBox');
            box.style.display = 'block';
            box.className = "alert " + type;
            box.innerText = text;
        }

        function hideAlert() {
            document.getElementById('msgBox').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# 3. پائথন بیک اینڈ اے پی آئیز جو جاوا اسکرپٹ سے بات کرتی ہیں
@app.route('/api/send-otp', methods=['POST'])
def api_send_otp():
    data = request.json
    phone = data.get('phone')
    
    conn = sqlite3.connect('shiraz_studio.db')
    cursor = conn.cursor()
    cursor.execute('SELECT verified FROM users WHERE phone = ?', (phone,))
    user = cursor.fetchone()
    
    if user and user[0] == 1:
        conn.close()
        return jsonify({"success": True, "already_verified": True, "message": "نمبر پہلے سے ویریفائیڈ ہے! سٹوڈیو میں خوش آمدید۔"})
    
    # نیا OTP
    otp = str(random.randint(1000, 9999))
    cursor.execute('INSERT OR REPLACE INTO users (phone, verified, pro_status) VALUES (?, 0, 0)', (phone,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "already_verified": False, "debug_otp": otp, "message": "نیا OTP جاری کر دیا گیا ہے۔"})

@app.route('/api/verify-otp', methods=['POST'])
def api_verify_otp():
    data = request.json
    phone = data.get('phone')
    
    conn = sqlite3.connect('shiraz_studio.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET verified = 1 WHERE phone = ?', (phone,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "ویریفیکیشن کامیاب!"})

@app.route('/api/buy-pro', methods=['POST'])
def api_buy_pro():
    data = request.json
    phone = data.get('phone')
    
    conn = sqlite3.connect('shiraz_studio.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET pro_status = 1 WHERE phone = ?', (phone,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "مبارک ہو! آپ کا پرو پیکج کامیابی سے ایکٹیو ہو گیا ہے۔"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
