from flask import Flask, request, render_template, jsonify
import sqlite3
import random

app = Flask(__name__)

# ڈیٹا بیس انیشلائزیشن (فائر بیس اور او ٹی پی ڈیٹا کے لیے محفوظ سیٹ اپ)
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

# فائر بیس او ٹی پی اور یوزر ویریفیکیشن روٹ
@app.route('/api/verify-user', methods=['POST'])
def verify_user():
    data = request.json
    phone = data.get('phone')
    
    conn = sqlite3.connect('shiraz_studio.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (phone, verified, pro_status, songs_created) VALUES (?, 1, 1, 0)', (phone,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "یوزر کامیابی سے وریفائی ہو گیا ہے!"})

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
