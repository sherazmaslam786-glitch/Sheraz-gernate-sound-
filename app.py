from flask import Flask, render_template
import os

app = Flask(__name__)
STUDIO_NAME = os.environ.get('STUDIO_NAME', 'Shiraz Pro AI Studio')

@app.route('/')
def index():
    return render_template('index.html', studio_name=STUDIO_NAME)

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
