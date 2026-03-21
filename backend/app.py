import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def mock_backend(path):
    hostname = os.environ.get("HOSTNAME", "unknown_host")
    return jsonify({
        "message": f"Hello from backend {hostname}!",
        "hostname": hostname,
        "requested_path": path,
        "note": "This hostname represents the unique ID of this Docker container replica."
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
