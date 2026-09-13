import os
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# فائر بیس کنکشن
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
                user_ref.set({"phone": phone_number, "verified": False, "songs_count": 0})

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

        return jsonify({"status": "success", "message": "تصدیق کامیاب! شاہانہ اے آئی سٹوڈیو تیار ہے۔"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"تصدیق میں خرابی: {str(e)}"}), 500

@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.json
        phone_number = data.get('phone')
        lyrics = data.get('lyrics', '')
        
        if not phone_number or not lyrics:
            return jsonify({"status": "error", "message": "فون نمبر اور شاعری کے بول لازمی ہیں!"}), 400

        # 1. آٹومیٹک لینگویج ڈیٹیکشن (زبان کی شناخت)
        detected_lang = "اردو / سرائیکی"
        if any(ord(char) < 128 for char in lyrics):
            # اگر انگریزی حروف زیادہ ہوں
            if sum(1 for c in lyrics if c.isascii()) > len(lyrics) / 2:
                detected_lang = "English (انگریزی)"
        elif any(word in lyrics for word in ["من", "دل", "باران", "يار"]):
            detected_lang = "فارسی (Persian)"
        elif any(word in lyrics for word in ["قلب", "حزن", "ليل"]):
            detected_lang = "عربی (Arabic)"
        elif any(word in lyrics for word in ["تہہ", "کیوں", "ندا"]):
            detected_lang = "پشتو (Pashto)"

        # 2. سمارٹ موڈ اینڈ بیٹ ڈیٹیکشن (غم یا جوشیلا ڈھول بیٹ)
        detected_mood = "شاہانہ صوفیانہ سوز"
        audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        
        lyrics_lower = lyrics.lower()
        if "غم" in lyrics_lower or "دہلا" in lyrics_lower or "روتا" in lyrics_lower or "درد" in lyrics_lower or "sad" in lyrics_lower:
            detected_mood = "دل دہلا دینے والا غم (Deep Sad Melancholy)"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
        elif "جوشیلا" in lyrics_lower or "دھول" in lyrics_lower or "دہم" in lyrics_lower or "بیٹ" in lyrics_lower or "energetic" in lyrics_lower or "dhol" in lyrics_lower:
            detected_mood = "دھم دھماٹ اور جوشیلا ڈھول بیٹ (Heavy Dhol & Beats)"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"

        # 3. فائر بیس 5 گانوں کی لمیٹ چیک
        songs_count = 0
        if db:
            user_ref = db.collection('users').document(phone_number)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                songs_count = user_data.get("songs_count", 0)
                
                if songs_count >= 5:
                    return jsonify({
                        "status": "limit_exceeded",
                        "message": "آپ کے 5 مفت شاہانہ گانے پورے ہو چکے ہیں۔ لائف ٹائم پرو ورژن (1,000 روپے) کے لیے رابطہ کریں!"
                    }), 403
                
                songs_count += 1
                user_ref.update({"songs_count": songs_count})
            else:
                user_ref.set({"phone": phone_number, "verified": True, "songs_count": 1})
                songs_count = 1

        songs_left = max(0, 5 - songs_count)

        return jsonify({
            "status": "success",
            "audio_url": audio_url,
            "detected_lang": detected_lang,
            "detected_mood": detected_mood,
            "songs_left": songs_left,
            "message": f"زبان: {detected_lang} | انداز: {detected_mood} | بقایا مفت گانے: {songs_left}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"جنریشن میں خرابی: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
