import os
from flask import Flask, render_template, request, jsonify
import fal_client

app = Flask(__name__)

# یہاں آپ کی Fal.ai API Key سیٹ کی گئی ہے
os.environ["FAL_KEY"] = os.environ.get("FAL_KEY", "d0edeae9-ebe8-48c8-ab59-0ad9a68b37ce:a51c38afb9b33450c7558f3eb79459e4")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'اردو میں تال اور موسیقی کے ساتھ ایک خوبصورت گانا')

        # Fal.ai API کو سبمٹ کرنے کا طریقہ
        handler = fal_client.submit(
            "fal-ai/stable-audio",
            arguments={
                "prompt": prompt,
                "seconds_total": 15
            }
        )
        
        result = handler.get()
        
        audio_url = None
        if isinstance(result, dict):
            if "audio_file" in result:
                audio_url = result["audio_file"].get("url")
            elif "audio" in result:
                audio_url = result["audio"].get("url")

        if audio_url:
            return jsonify({"status": "success", "audio_url": audio_url})
        else:
            return jsonify({"status": "error", "message": "مصنوعی ذہانت (AI) سے آڈیو کا لنک حاصل نہیں ہو سکاہے۔"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
 
