import json
import os
from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, initialize_app

app = Flask(__name__)

# فائر بیس کو Render کے Environment Variable سے کنیکٹ کرنا
firebase_creds_json = os.environ.get("FIREBASE_CREDENTIALS")
if firebase_creds_json:
  cred_dict = json.loads(firebase_creds_json)
  cred = credentials.Certificate(cred_dict)
  initialize_app(cred)


@app.route("/")
def home():
  return render_template("index.html")


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
