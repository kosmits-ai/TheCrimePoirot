from flask import Flask, request, jsonify
import subprocess
import requests
import os
import shutil
import json
import re
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

MONGODB_SERVICE_URL = os.getenv("MONGO_SERVICE_URL")
BASE_DIR = os.getenv("BASE_DIR", "/tmp/repos")

@app.route('/analyze', methods=['POST'])
def run_safety():
    
    repo_url = request.json.get("repo_url")
    if not repo_url:
        return jsonify({"status": "error", "tool": "safety", "message": "Repository URL is required", "data": None}), 400

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(BASE_DIR, repo_name)

    try:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)  # Remove existing repository in order to get the latest commit every time.
        
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)

        os.chdir(repo_path)
        print(f"Running Safety on {repo_path}...")

        result = subprocess.run(['safety', 'scan'], capture_output=True, text=True)

        # Process the output
        lines = result.stdout.splitlines()
        vulnerabilities = []  # List to hold vulnerability details

        for line in lines:
            # Match the package format: "package==version  [X vulnerabilities found]"
            package_match = re.search(r"^([\w\-]+)==([\d.]+).*?\[(\d+) vulnerabilit(?:y|ies) found(?:,.*)?\]", line.strip())

            if package_match:
                package_name = package_match.group(1)
                package_version = package_match.group(2)
                vuln_count = package_match.group(3)

                # Add the vulnerability details to the list
                vulnerabilities.append({
                    "package_name": package_name,
                    "version": package_version,
                    "vulnerabilities_found": int(vuln_count)
                })

        # Prepare the document to insert into MongoDB
        document = {
            "repo_name": repo_name,
            "vulnerabilities": vulnerabilities  # List of vulnerabilities or an empty list
        }

        response = requests.post(
            f"http://{MONGODB_SERVICE_URL}/safety/insert",
            json=document
        )

        if response.status_code != 200:
            return jsonify({"status": "error", "tool": "safety", "message": "Failed to store results in MongoDB", "data": None}), 500

        print(f"Results stored for repo {repo_name}: {document}")

        return jsonify({
            "status": "success",
            "tool": "safety",
            "message": "Analysis complete",
            "data": document
        }), 200

    except FileNotFoundError as e:
        return jsonify({"status": "error", "tool": "safety", "message": f"The directory {repo_path} does not exist: {str(e)}", "data": None}), 404
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "tool": "safety", "message": f"Error running safety scan: {e.stderr}", "data": None}), 500
    except Exception as e:
        return jsonify({"status": "error", "tool": "safety", "message": f"An unexpected error occurred: {str(e)}", "data": None}), 500