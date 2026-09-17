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
            return jsonify({"success": False, "error": "لیرکس خالی ہیں! براہ کرم بول درج کریں۔"}), 400

        # یہاں لیرکس اور وائس اسٹائل کامیابی سے ریسیو ہو رہے ہیں
        print(f"[جنریشن انجن] موصولہ بول: {lyrics}")
        print(f"[جنریشن انجن] منتخب کردہ انداز: {voice_style}")

        # جب آپ اس میں اصلی اے آئی جنریشن پائپ لائن یا API پلگ ان کریں گے، 
        # تو تیار شدہ آڈیو کا لنک یہاں سے ریٹرن ہوگا۔
        output_audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"

        return jsonify({
            "success": True,
            "message": "گانا کامیابی سے تیار ہو گیا ہے!",
            "audio_url": output_audio_url
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
