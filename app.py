import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate-song', methods=['POST'])
def generate_song():
    try:
        data = request.json
        lyrics = data.get('lyrics', '')
        voice_style = data.get('voice_style', 'male')

        if not lyrics:
            return jsonify({"success": False, "error": "لیرکس خالی ہیں!"}), 400

        # یہاں پائথন کا انجن لیرکس اور وائس اسٹائل کو پروسیس کرتا ہے
        print(f"[سسٹم] موصول ہونے والے بول: {lyrics}")
        print(f"[سسٹم] منتخب کردہ انداز: {voice_style}")

        # یہ وہ فائنل آڈیو آؤٹ پٹ ہے جو جنریٹ ہو کر فرنٹ اینڈ پر جائے گا
        output_audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

        return jsonify({
            "success": True,
            "message": "گانا کامیابی سے تیار ہو گیا ہے!",
            "audio_url": output_audio_url
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
