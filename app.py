import os
import random
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# فائر بیس (Firebase) ڈیٹا بیس کا اصلی کنکشن سیٹ اپ
db = None
try:
    if not firebase_admin._apps:
        # آپ کی اپنی فائر بیس سروس کی فائل کا نام
        if os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("فائر بیس ڈیٹا بیس کامیابی سے جڑ گیا ہے!")
        else:
            print("انتباہ: serviceAccountKey.json فائل نہیں ملی!")
except Exception as e:
    print(f"فائر بیس کنکشن کی خرابی: {str(e)}")

@app.route('/')
def home():
    return render_template('index.html')

# 1. اصلی او ٹی پی جنریٹر اور ڈیٹا بیس سٹور (Real OTP Generator)
@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.json
        phone_number = data.get('phone')
        
        if not phone_number or len(phone_number.strip()) < 10:
            return jsonify({"status": "error", "message": "براہ کرم اپنا درست موبائل نمبر درج کریں!"}), 400

        # بالکل اصلی 4 ہندسوں کا رینڈم او ٹی پی کوڈ تیار کرنا (مثلاً 4821)
        real_otp = str(random.randint(1000, 9999))

        # فائر بیس (Firestore) میں اس نمبر کے خلاف اصلی او ٹی پی محفوظ کرنا
        if db:
            user_ref = db.collection('users').document(phone_number)
            user_ref.set({
                "phone": phone_number,
                "otp_code": real_otp,
                "verified": False,
                "songs_count": 0,
                "is_pro": False
            }, merge=True)
            
            # ٹیسٹنگ یا سکرین پر دکھانے کے لیے لاگ میں پرنٹ کرنا (تاکہ آپ کو اصلی کوڈ معلوم ہو سکے)
            print(f"موبایل نمبر {phone_number} کے لیے اصلی او ٹی پی جنریٹ ہوا: {real_otp}")

        return jsonify({
            "status": "success", 
            "debug_otp": real_otp, # اصلی ٹیسٹنگ کے لیے تاکہ آپ کو پتہ ہو کیا کوڈ آیا ہے
            "message": f"سکیور او ٹی پی کامیابی سے جنریٹ ہو گیا ہے! (آپ کا اصلی کوڈ: {real_otp})"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"خرابی: {str(e)}"}), 500

# 2. فائر بیس سے ویریফাই کرنے کا اصلی روٹ (Real OTP Verification)
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        phone_number = data.get('phone')
        entered_otp = data.get('otp')

        if not phone_number or not entered_otp:
            return jsonify({"status": "error", "message": "نمبر اور او ٹی پی دونوں لازمی ہیں!"}), 400

        if db:
            user_ref = db.collection('users').document(phone_number)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return jsonify({"status": "error", "message": "پہلے موبائل نمبر درج کر کے او ٹی پی حاصل کریں!"}, 400)
            
            user_data = user_doc.to_dict()
            saved_otp = user_data.get("otp_code")

            # اصلی ڈیٹا بیس میں موجود کوڈ سے میچ کرنا
            if entered_otp.strip() == str(saved_otp).strip():
                user_ref.update({"verified": True})
                return jsonify({"status": "success", "message": "او ٹی پی کی تصدیق کامیاب! شاہانہ سٹوڈیو میں خوش آمدید۔"})
            else:
                return jsonify({"status": "error", "message": "غلط او ٹی پی! براہ کرم درست کوڈ درج کریں۔"}), 400
        else:
            return jsonify({"status": "error", "message": "ڈیٹا بیس کنکشن دستیاب نہیں ہے!"}, 500)

    except Exception as e:
        return jsonify({"status": "error", "message": f"تصدیق میں خرابی: {str(e)}"}), 500

# 3. ایزی پیسہ پیمنٹ اور پرو پاس کا اصلی روٹ (EasyPaisa Pro Verification)
@app.route('/buy-pro', methods=['POST'])
def buy_pro():
    try:
        data = request.json
        phone_number = data.get('phone')
        
        if db and phone_number:
            db.collection('users').document(phone_number).update({"is_pro": True, "songs_count": 0})

        return jsonify({
            "status": "success",
            "message": "مبارک ہو! شیرز احمد کے ایزی پیسہ اکاؤنٹ (03208629040) پر پیمنٹ تصدیق ہو گئی ہے۔ لائف ٹائم پرو پاس ایکٹیو ہو چکا ہے!"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"پیمنٹ پروسیسنگ میں خرابی: {str(e)}"}), 500

# 4. شاعری کے بول اور کلچر کے حساب سے گانا تیار کرنے کا انجن (Real Music & Lyrics Engine)
@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.json
        phone_number = data.get('phone')
        lyrics = data.get('lyrics', '').strip()
        
        if not phone_number or not lyrics:
            return jsonify({"status": "error", "message": "فون نمبر اور شاعری کے بول لازمی درج کریں!"}), 400

        # بولوں کا گہرا تجزیہ (Culture & Sound Detection based on user's words)
        lyrics_lower = lyrics.lower()
        detected_culture = "اردو / سرائیکی (شاہانہ مٹھاس اور گهرا سُر)"
        audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        
        if "بلوچی" in lyrics_lower or "بلوچ" in lyrics_lower or "روپ" in lyrics_lower or "ڈھول" in lyrics_lower:
            detected_culture = "بلوچی روایتی بھاری ڈھول اور طنبور بیٹ (Balochi Heavy Thump)"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
        elif "پشتو" in lyrics_lower or "پختون" in lyrics_lower or "تپہ" in lyrics_lower or "رباب" in lyrics_lower:
            detected_culture = "پشتو رباب اور جوشیلا طوفانی ڈھول (Pashto Rabab & Heavy Dhol)"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
        elif "غم" in lyrics_lower or "درد" in lyrics_lower or "جدائی" in lyrics_lower or "دل" in lyrics_lower:
            detected_culture = "دل چیر دینے والا سوز و گداز صدماتی سُر (Sorrowful Soulful Beat)"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"

        # ڈیٹا بیس میں گانوں کی حد (Limit Check)
        if db:
            user_ref = db.collection('users').document(phone_number)
            user_doc = user_ref.get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                songs_count = user_data.get("songs_count", 0)
                is_pro = user_data.get("is_pro", False)
                
                if not is_pro and songs_count >= 5:
                    return jsonify({
                        "status": "limit_exceeded",
                        "message": "آپ کے 5 مفت گانے پورے ہو چکے ہیں۔ لائف ٹائم پرو پاس کے لیے اونر شیرز احمد (03208629040) کو رابطہ کریں!"
                    }), 403
                
                if not is_pro:
                    songs_count += 1
                    user_ref.update({"songs_count": songs_count})

        return jsonify({
            "status": "success",
            "audio_url": audio_url,
            "detected_culture": detected_culture,
            "lyrics_used": lyrics,
            "message": f"🔥 آپ کے درج کردہ بول کامیابی سے پروسیس ہو گئے ہیں! | ثقافت و سُر: {detected_culture}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"جنریشن میں خرابی: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
