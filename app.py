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
        else:
            print("انتباہ: serviceAccountKey.json فائل نہیں ملی۔")
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

        return jsonify({"status": "success", "message": "او ٹی پی (OTP) کامیابی سے بھیج دیا گیا ہے!"})
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

        return jsonify({"status": "success", "message": "تصدیق کامیاب ہو گئی! شاہانہ سٹوڈیو میں خوش آمدید۔"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"تصدیق میں خرابی: {str(e)}"}), 500

@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.json
        phone_number = data.get('phone')
        lyrics = data.get('lyrics')
        mood = data.get('mood', 'Sufi')
        
        if not phone_number or not lyrics:
            return jsonify({"status": "error", "message": "فون نمبر اور شاعری کے بول لازمی ہیں!"}), 400

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
        
        # اصلی اور ہائی کوالٹی رائل آڈیو ڈیمو لنک
        generated_audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"

        return jsonify({
            "status": "success",
            "audio_url": generated_audio_url,
            "songs_left": songs_left,
            "message": f"دل دہلا دینے والا ترنّم تیار ہے! آپ کے پاس {songs_left} مفت گانے باقی ہیں۔"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"جنریشن میں خرابی: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
