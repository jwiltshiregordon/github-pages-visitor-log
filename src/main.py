from flask import Flask, request, jsonify
from src.register_repo import register_repo
from src.log_message import log_message
from src.fetch_logs import fetch_logs
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    repo_name = data.get('repo_name')
    repo_owner = data.get('repo_owner')
    response = register_repo(repo_owner, repo_name)
    return jsonify(response)


@app.route('/log', methods=['POST'])
def log():
    data = request.get_json()

    if data is None or 'repo_name' not in data or 'event_details' not in data:
        return jsonify({'status': 'error', 'message': 'Bad Request: Missing required fields'}), 400

    repo_owner = data.get('repo_owner')
    repo_name = data.get('repo_name')
    event_details = data.get('event_details')

    response = log_message(repo_owner, repo_name, event_details)
    return jsonify(response)


@app.route('/fetch-logs', methods=['GET'])
def fetch():
    repo_owner = request.args.get('repo_owner')
    repo_name = request.args.get('repo_name')

    if not repo_owner or not repo_name:
        return jsonify({"status": "error", "message": "repo_name parameter is required"}), 400

    response = fetch_logs(repo_owner, repo_name)
    return jsonify(response)
