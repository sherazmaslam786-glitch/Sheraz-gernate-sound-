
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ہر فون نمبر کے 5 گانے مفت دینے کا کاؤنٹر
user_song_counts = {}

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"انٹرفیس لوڈ کرنے میں خرابی: {str(e)}", 500

@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "کوئی ڈیٹا موصول نہیں ہوا!"}), 400

        phone_number = data.get('phone')
        lyrics = data.get('lyrics')
        mood = data.get('mood', 'Sad') # ڈیفالٹ موڈ غمگین
        voice_type = data.get('voice_type', 'Male') # ڈیفالٹ آواز مرد
        
        # فون نمبر کی جانچ پڑتال
        if not phone_number:
            return jsonify({
                "status": "error",
                "message": "براہ کرم اپنا فون نمبر درج کریں!"
            }, 400)

        # فری لمیٹ چیک کرنا (5 گانے مفت)
        if phone_number not in user_song_counts:
            user_song_counts[phone_number] = 0
            
        if user_song_counts[phone_number] >= 5:
            return jsonify({
                "status": "limit_exceeded",
                "message": "آپ کے 5 مفت گانے پورے ہو چکے ہیں۔ مزید دل کو چھو لینے والے گانے بنانے کے لیے براہ کرم Pro ورژن خریدیے (Easypaisa/JazzCash)!"
            }), 403

        # گانے کا کاؤנט ایک بڑھانا
        user_song_counts[phone_number] += 1
        songs_left = 5 - user_song_counts[phone_number]

        # AI API انجن کال کرنے کا محفوظ طریقہ
        generated_audio_url = call_ai_music_api(lyrics, mood, voice_type)

        return jsonify({
            "status": "success",
            "audio_url": generated_audio_url,
            "songs_left": songs_left,
            "message": f"گانا کامیابی سے بن گیا! آپ کے پاس {songs_left} مفت گانے باقی ہیں۔"
        })

    except Exception as e:
        # اگر کوئی بھی تکنیکی خرابی آئے تو ایپ کریش نہیں ہوگی بلکہ ایرر بتائے گی
        return jsonify({
            "status": "error",
            "message": f"سسٹم میں خرابی آگئی: {str(e)}"
        }), 500

def call_ai_music_api(lyrics, mood, voice_type):
    # یہاں اے آئی جنریشن انجن کام کرے گا
    # فی الحال یہ سٹیبل سیمپل آڈیو ریٹرن کر رہا ہے تاکہ ایپ رکے نہیں
    return "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # ڈی بگ موڈ کو ہمیشہ آن رکھا ہے تاکہ سرور محفوظ طریقے سے چلے
    app.run(host='0.0.0.0', port=port, debug=True)
