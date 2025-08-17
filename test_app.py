from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        'status': 'success',
        'message': 'Flask app is working on Vercel!',
        'test': 'minimal app running'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# Vercel entry point
application = app

if __name__ == "__main__":
    app.run(debug=True)
