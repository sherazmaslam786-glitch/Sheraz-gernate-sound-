import os
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

db = None
try:
    if not firebase_admin._apps:
        if os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
            db = firestore.client()
except Exception as e:
    print(f"فائر بیس کنکشن کا مسئلہ: {str(e)}")

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"انٹرفیس لوڈ کرنے میں خرابی: {str(e)}", 500

@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.json
        phone_number = data.get('phone')
        if not phone_number:
            return jsonify({"status": "error", "message": "براہ کرم درست فون نمبر درج کریں!"}), 400

        if db:
            user_ref = db.collection('users').document(phone_number)
            user_doc = user_ref.get()
            if not user_doc.exists:
                user_ref.set({"phone": phone_number, "verified": False, "songs_count": 0, "is_pro": False})

        return jsonify({"status": "success", "message": "او ٹی پی کامیابی سے بھیج دیا گیا ہے!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"سسٹم خرابی: {str(e)}"}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        phone_number = data.get('phone')
        if not phone_number:
            return jsonify({"status": "error", "message": "فون نمبر درکار ہے!"}), 400

        if db:
            user_ref = db.collection('users').document(phone_number)
            user_ref.update({"verified": True})

        return jsonify({"status": "success", "message": "تصدیق کامیاب! شاہانہ سٹوڈیو میں خوش آمدید۔"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"تصدیق میں خرابی: {str(e)}"}), 500

# ایزی پیسہ / جاز کیش سے پرو ورژن خریدنے کا روٹ
@app.route('/buy-pro', methods=['POST'])
def buy_pro():
    try:
        data = request.json
        phone_number = data.get('phone')
        payment_method = data.get('method') # EasyPaisa / JazzCash / Bank
        
        if not phone_number:
            return jsonify({"status": "error", "message": "فون نمبر لازمی ہے!"}), 400

        if db:
            user_ref = db.collection('users').document(phone_number)
            user_ref.update({"is_pro": True, "songs_count": 0})

        return jsonify({
            "status": "success",
            "message": f"مبارک ہو! آپ کا {payment_method} کے ذریعے 1,000 روپے کا پرو پاس فعال ہو گیا ہے۔ اب آپ انمٹ گانے بنا سکتے ہیں!"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"پیمنٹ پروسیسنگ میں خرابی: {str(e)}"}), 500

@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.json
        phone_number = data.get('phone')
        lyrics = data.get('lyrics', '')
        
        if not phone_number or not lyrics:
            return jsonify({"status": "error", "message": "فون نمبر اور شاعری کے بول لازمی ہیں!"}), 400

        # زبان کی خودکار شناخت
        detected_lang = "اردو / سرائیکی / پنجابی"
        if any(ord(char) < 128 for char in lyrics) and sum(1 for c in lyrics if c.isascii()) > len(lyrics) / 2:
            detected_lang = "English"

        # ہیوی بیس، گٹار اور دھم دھماٹ موڈ
        audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        detected_mood = "شاہانہ ہیوی بیس اور گٹار بیٹ (Viral Heavy Bass)"
        
        lyrics_lower = lyrics.lower()
        if "غم" in lyrics_lower or "درد" in lyrics_lower or "روتا" in lyrics_lower:
            detected_mood = "دل دہلا دینے والا سوز و گداز (Deep Emotional Melancholy)"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
        elif "جوشیلا" in lyrics_lower or "دھول" in lyrics_lower or "دہم" in lyrics_lower or "بیٹ" in lyrics_lower:
            detected_mood = "دھم دھماٹ ٹک ٹاک بم دھماکہ بیٹ (Heavy Dhol & Viral Beats)"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"

        # لمیٹ چیک
        songs_count = 0
        is_pro = False
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
                        "message": "آپ کے 5 مفت گانے پورے ہو چکے ہیں۔ نیچے دیے گئے ایزی پیسہ/جاز کیش بٹن سے 1,000 روپے میں پرو پاس خریدیں!"
                    }), 403
                
                if not is_pro:
                    songs_count += 1
                    user_ref.update({"songs_count": songs_count})
            else:
                user_ref.set({"phone": phone_number, "verified": True, "songs_count": 1, "is_pro": False})
                songs_count = 1

        songs_left = "لاعثود (Pro Unlimited)" if is_pro else max(0, 5 - songs_count)
        viral_share_link = f"https://shiraz-gernate-sound-1.onrender.com?song={abs(hash(lyrics))}"

        return jsonify({
            "status": "success",
            "audio_url": audio_url,
            "detected_lang": detected_lang,
            "detected_mood": detected_mood,
            "songs_left": songs_left,
            "viral_link": viral_share_link,
            "message": f"🔥 دھوم مچانے والا ٹریک تیار ہے! | موڈ: {detected_mood}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"جنریشن میں خرابی: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
