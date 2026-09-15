from flask import Flask, request, render_template, jsonify
import sqlite3
import random

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('shiraz_studio.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            verified INTEGER DEFAULT 0,
            pro_status INTEGER DEFAULT 0,
            songs_created INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/send-otp', methods=['POST'])
def api_send_otp():
    data = request.json
    phone = data.get('phone')
    otp = str(random.randint(1000, 9999))
    conn = sqlite3.connect('shiraz_studio.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (phone, verified, pro_status) VALUES (?, 0, 0)', (phone,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "otp": otp})

if __name__ == '__main__':
    app.run(debug=True)
    
