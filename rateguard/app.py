import os
from flask import Flask, request, jsonify
from .middleware import check_rate_limit
from .proxy import forward_request

app = Flask(__name__)

@app.before_request
def rate_limit_middleware():
    # Identify user (IP or API key) and endpoint
    # Since RateGuard is behind an NGINX proxy, extract the true client IP from X-Forwarded-For
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        user_id = x_forwarded_for.split(',')[0].strip()
    else:
        user_id = request.remote_addr or "anonymous"
        
    endpoint = request.path

    # Check if request is allowed
    is_allowed = check_rate_limit(user_id, endpoint)
    
    if not is_allowed:
        return jsonify({"error": "Too Many Requests. Rate limit exceeded."}), 429

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_all(path):
    return forward_request()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
