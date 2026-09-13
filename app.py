import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# عارضی طور پر فائر بیس اور او ٹی پی ڈیٹا کو سنبھالنے والا سٹرکچر
# (اگلے مرحلے میں ہم اس کے ساتھ فائر بیس کی اصل لائبریری 'firebase_admin' جوڑیں گے)
user_database = {}

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"انٹرفیس لوڈ کرنے میں خرابی: {str(e)}", 500

# 1. او ٹی پی بھیجنے کا روٹ (OTP Send API)
@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.json
        phone_number = data.get('phone')
        
        if not phone_number:
            return jsonify({"status": "error", "message": "براہ کرم درست فون نمبر درج کریں!"}), 400

        # یہاں ہم فائر بیس یا ایس ایم ایس گیٹ وے کے ذریعے او ٹی پی جنریٹ کر کے بھیجیں گے
        # فی الحال ٹیسٹنگ کے لیے او ٹی پی '1234' سیٹ کر رہے ہیں
        user_database[phone_number] = {"otp": "1234", "verified": False, "songs_count": 0}

        return jsonify({
            "status": "success",
            "message": "او ٹی پی کامیابی سے بھیج دیا گیا ہے! (مفت ٹیسট کوڈ: 1234)"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 2. او ٹی پی وریفائی کرنے کا روٹ (OTP Verify API)
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        phone_number = data.get('phone')
        entered_otp = data.get('otp')

        if phone_number in user_database and user_database[phone_number]["otp"] == entered_otp:
            user_database[phone_number]["verified"] = True
            return jsonify({"status": "success", "message": "فون نمبر کامیابی سے وریفائی ہو گیا ہے!"})
        else:
            return jsonify({"status": "error", "message": "غلط او ٹی پی! براہ کرم دوبارہ کوشش کریں۔"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. گانا جنریٹ کرنے کا اصل انجن (AI Music & Freemium Counter)
@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "کوئی ڈیٹا موصول نہیں ہوا!"}), 400

        phone_number = data.get('phone')
        lyrics = data.get('lyrics')
        mood = data.get('mood', 'Sad')
        voice_type = data.get('voice_type', 'Male')
        
        if not phone_number or phone_number not in user_database:
            return jsonify({"status": "error", "message": "پہلے اپنے فون نمبر کی تصدیق (OTP) کروائیں!"}), 400

        # چیک کریں کہ آیا یوزر وریفائیڈ ہے
        if not user_database[phone_number].get("verified", False):
            return jsonify({"status": "error", "message": "آپ کا فون نمبر وریفائیڈ نہیں ہے!"}), 403

        # 5 گانے مفت کی لمیٹ چیک کرنا
        current_songs = user_database[phone_number]["songs_count"]
        if current_songs >= 5:
            return jsonify({
                "status": "limit_exceeded",
                "message": "آپ کے 5 مفت گانے پورے ہو چکے ہیں۔ مزید دل کو چھو لینے والے گانے بنانے کے لیے براہ کرم EasyPaisa/JazzCash سے Pro ورژن خریدیے!"
            }), 403

        # گانے کا کاؤנט ایک بڑھانا
        user_database[phone_number]["songs_count"] += 1
        songs_left = 5 - user_database[phone_number]["songs_count"]

        # اے آئی میوزک انجن کال فنکشن
        generated_audio_url = call_ai_music_api(lyrics, mood, voice_type)

        return jsonify({
            "status": "success",
            "audio_url": generated_audio_url,
            "songs_left": songs_left,
            "message": f"گانا کامیابی سے بن گیا! آپ کے پاس {songs_left} مفت گانے باقی ہیں۔"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"سسٹم میں خرابی آگئی: {str(e)}"}), 500

def call_ai_music_api(lyrics, mood, voice_type):
    # اے آئی میوزک جنریشن کا اے پی آئی ہک
    return "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
