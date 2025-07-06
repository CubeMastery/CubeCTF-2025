from flask import Flask, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')

@app.route('/script.js')
def script():
    response = send_file("script.js", mimetype="application/javascript")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
@app.route('/index.html')
def home():
    response = send_file("index.html", mimetype="text/html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True, port=9000, host='0.0.0.0')