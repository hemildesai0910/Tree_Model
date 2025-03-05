from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

def get_github_repo_tree(repo_url):
    """Fetch the GitHub repo tree and return a structured JSON response."""
    path = urlparse(repo_url).path.strip('/')
    parts = path.split('/')

    if len(parts) < 2:
        return {"error": "Invalid GitHub URL"}, 400

    owner, repo = parts[0], parts[1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url)

    if response.status_code != 200:
        return {"error": "Repository not found or private"}, response.status_code

    default_branch = response.json().get('default_branch', 'main')
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
    tree_response = requests.get(tree_url)

    if tree_response.status_code != 200:
        return {"error": "Unable to fetch repository tree"}, tree_response.status_code

    tree_data = tree_response.json()
    if tree_data.get('truncated', False):
        return {"warning": "Tree is truncated, results may be incomplete"}, 206

    return {"repository": f"{owner}/{repo}", "branch": default_branch, "tree": tree_data.get("tree", [])}

@app.route('/get-repo-tree', methods=['POST'])
def repo_tree():
    data = request.get_json()
    repo_url = data.get("repo_url")
    if not repo_url:
        return jsonify({"error": "Repository URL is required"}), 400

    result = get_github_repo_tree(repo_url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
