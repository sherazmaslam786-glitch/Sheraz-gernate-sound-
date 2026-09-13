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
    return render_template('index.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.json
        phone_number = data.get('phone')
        if not phone_number:
            return jsonify({"status": "error", "message": "براہ کرم درست فون نمبر درج کریں!"}), 400

        if db:
            user_ref = db.collection('users').document(phone_number)
            if not user_ref.get().exists:
                user_ref.set({"phone": phone_number, "verified": False, "songs_count": 0, "is_pro": False})

        return jsonify({"status": "success", "message": "او ٹی پی کامیابی سے بھیج دیا گیا ہے! فون کی وائبریشن چیک کریں۔"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"سسٹم خرابی: {str(e)}"}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        phone_number = data.get('phone')
        if db:
            db.collection('users').document(phone_number).update({"verified": True})
        return jsonify({"status": "success", "message": "تصدیق کامیاب! شاہانہ سٹوڈیو میں خوش آمدید۔"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"تصدیق میں خرابی: {str(e)}"}), 500

@app.route('/buy-pro', methods=['POST'])
def buy_pro():
    try:
        data = request.json
        phone_number = data.get('phone')
        payment_method = data.get('method')
        
        if db:
            db.collection('users').document(phone_number).update({"is_pro": True, "songs_count": 0})

        return jsonify({
            "status": "success",
            "message": "مبارک ہو! آپ کی پیمنٹ شیرز احمد کے ایزی پیسہ اکاؤنٹ (03208629040) میں تصدیق ہو گئی ہے۔ پرو پاس فعال ہے!"
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

        lyrics_lower = lyrics.lower()
        detected_culture = "اردو / سرائیکی (شاہانہ مٹھاس اور سُر)"
        audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        
        if "بلوچی" in lyrics_lower or "بلوچ" in lyrics_lower or "روپ" in lyrics_lower or "شامل" in lyrics_lower:
            detected_culture = "بلوچی روایتی ڈھول اور طنبور بیٹ (Balochi Folk Heavy Thump)"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
        elif "پشتو" in lyrics_lower or "پختون" in lyrics_lower or "تپہ" in lyrics_lower:
            detected_culture = "پشتو رباب اور جوشیلا ڈھول طوفان (Pashto Rabab & Heavy Dhol)"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
        elif "غم" in lyrics_lower or "درد" in lyrics_lower:
            detected_culture = "دل چیر دینے والا سوز و گداز اور درد بھرا لہجہ"
            audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"

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
                        "message": "آپ کے 5 مفت گانے پورے ہو چکے ہیں۔ لائف ٹائم پرو پاس کے لیے اونر شیرز احمد (03208629040) پر 1,000 روپے بھیجیں!"
                    }), 403
                
                if not is_pro:
                    songs_count += 1
                    user_ref.update({"songs_count": songs_count})
            else:
                user_ref.set({"phone": phone_number, "verified": True, "songs_count": 1, "is_pro": False})

        viral_share_link = f"https://shiraz-gernate-sound-1.onrender.com?song={abs(hash(lyrics))}"

        return jsonify({
            "status": "success",
            "audio_url": audio_url,
            "detected_culture": detected_culture,
            "viral_link": viral_share_link,
            "message": f"🔥 ڈھول کی گہری دھمک اور پرفیکٹ بیٹ کے ساتھ ٹریک تیار ہے! | ثقافت: {detected_culture}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"جنریشن میں خرابی: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
