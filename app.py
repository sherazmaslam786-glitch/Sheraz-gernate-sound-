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
            return jsonify({"success": False, "error": "براہ کرم گانے کے بول (لیرکس) درج کریں!"}), 400

        print(f"[موصولہ لیرکس]: {lyrics}")
        print(f"[منتخب کردہ اسٹائل]: {voice_style}")

        # گائیکی کے انداز (Voice Style) کے حساب سے آڈیو ٹریکس کے لنکس
        audio_map = {
            "male": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            "female": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            "sufi": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
        }

        # جو اسٹائل یوزر نے چُنا ہے، اس کا لنک سلیکٹ ہو جائے گا
        selected_audio = audio_map.get(voice_style, audio_map["male"])

        return jsonify({
            "success": True,
            "message": "گانا کامیابی سے تیار ہو گیا ہے!",
            "audio_url": selected_audio
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
    
