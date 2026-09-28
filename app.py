from flask import Flask, request, jsonify
from gradio_client import Client
import os

app = Flask(__name__)

# آپ کا گوگل کولاب والا مفت پبلک لنک یہاں سیٹ کر دیا گیا है
COLAB_GRADIO_URL = "https://fa4ca99a34de575b22.gradio.live"

@app.route('/generate-music', methods=['POST'])
def generate_music():
    data = request.get_json()
    prompt = data.get('prompt', 'upbeat electronic dance track')
    
    try:
        # گوگل کولاب والے مفت سرور سے رابطہ کریں
        client = Client(COLAB_GRADIO_URL)
        
        # اے آئی ماڈل کو پرامپٹ بھیج کر گانا تیار کروائیں
        result = client.predict(
            prompt_text=prompt,
            api_name="/predict"
        )
        
        # تیار شدہ آڈیو/گانے کی فائل کا لنک یا پاتھ واپس بھیجیں
        return jsonify({"success": True, "audio_url": result})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
