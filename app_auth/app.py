from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route('/health')
def health():
    return jsonify({"status": "UP", "service": "auth-service"}), 200

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    return jsonify({"message": "User authenticated successfully", "token": "jwt-token-xyz-123"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
