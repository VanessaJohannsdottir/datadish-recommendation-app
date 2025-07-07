from flask import Flask, request, jsonify
import jamspell
from waitress import serve

app = Flask(__name__)
speller = jamspell.TSpellCorrector()
speller.LoadLangModel('model/en.bin')

@app.route('/clean', methods=['POST'])
def clean():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" field'}), 400

    text = data['text']
    cleaned = speller.FixFragment(text)
    return jsonify({'corrected': cleaned})

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
