from flask import Flask, render_template
import threading, webbrowser
from instagram import instagram_bp
from x import twitter_bp
from facebook import facebook_bp
from youtube import youtube_bp
from tiktok import tiktok_bp

app = Flask(__name__, template_folder="templates")

# Register Blueprints
app.register_blueprint(instagram_bp)
app.register_blueprint(twitter_bp, url_prefix='/twitter')
app.register_blueprint(facebook_bp)
app.register_blueprint(youtube_bp)
app.register_blueprint(tiktok_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/instagram')
def instagram():
    return render_template('instagram.html')

@app.route('/twitter')
def x():
    return render_template('x.html')

@app.route('/facebook')
def facebook():
    return render_template('facebook.html')

@app.route('/youtube')
def youtube():
    return render_template('youtube.html')

@app.route('/tiktok')
def tiktok():
    return render_template('tiktok.html')

if __name__ == '__main__':
    def open_browser():
        webbrowser.open("http://127.0.0.1:5000")
    threading.Timer(1, open_browser).start()
    
    app.run(debug=True)
