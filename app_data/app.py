from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "UP", "service": "data-service"}), 200

@app.route('/api/v1/data/metrics')
def metrics():
    db_host = os.getenv('DB_HOST', 'localhost')
    return jsonify({"service": "data-service", "database_connected": db_host, "status": "active"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
