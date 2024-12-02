from flask import Flask, render_template, request, jsonify, Response, send_from_directory
import json
import logging

from services.ollama_utils import fetch_models
from services.search import process_search

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/')
def index():
    logging.info("Rendering index page")
    models = fetch_models()
    logging.info(f"Fetched models")
    return render_template('index.html', models=models)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    model = request.form['model']
    quickSearch_en = request.form.get('quickSearch_enable') == 'true'

    logging.info(f"Received search query: {query} with model: {model}")
    logging.info(f"Quick Search enabled: {quickSearch_en}")

    try:
        results = process_search(query, model,quickSearch_en)
        logging.info(f"Processed search query successfully")
        return jsonify(results)
    except Exception as e:
        logging.error(f"Failed to process search query: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/service-worker.js')
def service_worker():
    logging.info("Serving service-worker.js")
    return send_from_directory('static/js', 'service-worker.js')

@app.route('/manifest.json')
def manifest():
    logging.info("Serving manifest.json")
    return send_from_directory('static', 'manifest.json')

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)