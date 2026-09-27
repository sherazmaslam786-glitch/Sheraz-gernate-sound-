import os
from flask import Flask, render_template, request, jsonify
import fal_client

app = Flask(__name__)

# Render environment se FAL_KEY khud ba khud uth jaye gi
os.environ["FAL_KEY"] = os.environ.get("FAL_KEY", "d0edeae9-ebe8-48c8-ab59-0ad9a68b37ce:a51c38afb9b33450c7558f3eb79459e4")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'A beautiful song in Urdu with rhythm and music')

        # Fal.ai ka stable-audio model call karna
        handler = fal_client.submit(
            "fal-ai/stable-audio",
            arguments={
                "prompt": prompt,
                "seconds_total": 30
            }
        )
        
        result = handler.get()
        audio_url = result.get("audio_file", {}).get("url") if isinstance(result, dict) else None

        if audio_url:
            return jsonify({"status": "success", "audio_url": audio_url})
        else:
            return jsonify({"status": "error", "message": "AI se audio URL hasil nahi ho saka."}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
