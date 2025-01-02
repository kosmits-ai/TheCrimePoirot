from flask import Flask, request, jsonify
import os
import subprocess
import shutil
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
import json 

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)


MONGODB_SERVICE_URL = os.getenv("MONGO_SERVICE_URL")
GITLEAKS_PATH = os.getenv("GITLEAKS_PATH")
BASE_DIR = os.getenv("BASE_DIR")

# Validate critical environment variables
if not all([GITLEAKS_PATH, BASE_DIR, MONGODB_SERVICE_URL]):
    raise EnvironmentError("Missing required environment variables. Ensure GITLEAKS_PATH, BASE_DIR, and MONGODB_SERVICE_URL are set.")

@app.route('/analyze',methods=['POST'])
    """
    Run Gitleaks on a repository and store the results in MongoDB.
    """
    repo_url = request.json.get("repo_url")
    if not repo_url:
        return jsonify({"status": "error", "message": "Repository URL is required"}), 400
    
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(BASE_DIR, repo_name)
    report_path = os.path.join(repo_path, 'gitleaks.json')

    try:
        
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)  # Remove existing repository and clone it every time in order to get the latest commit.
        
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)


        if not os.path.isfile(GITLEAKS_PATH):
            return jsonify({
                "status": "error",
                "tool": "gitleaks",
                "message": f"Gitleaks executable not found at {GITLEAKS_PATH}",
                "data": None
            }), 404

        # Run Gitleaks
        result = subprocess.run(
            [GITLEAKS_PATH, 'detect', '--source', repo_path, '--report-format', 'json', '--report-path', report_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # No leaks found
            document = {"repo_name": repo_name, "leaks": []}
        
        elif result.returncode == 1 and os.path.exists(report_path):
            # Leaks found
            with open(report_path, 'r') as report_file:
                leaks_data = report_file.read()

            try:
                leaks_list = json.loads(leaks_data)  # Parse the JSON into a list of leaks
            except json.JSONDecodeError:
                leaks_list = [leak.strip() for leak in leaks_data.splitlines() if leak.strip()]

            document = {"repo_name": repo_name, "leaks": leaks_list}
        
        else:
            # Gitleaks error
            return jsonify({
                "status": "error",
                "tool": "gitleaks",
                "message": f"Gitleaks failed: {result.stderr.strip()}",
                "data": None
            }), 500

        #Post results to gitleaks collection.
        response = requests.post(
            f"http://{MONGODB_SERVICE_URL}/gitleaks/insert",
            json=document                                       
        )

        return jsonify({
            "status": "success",
            "tool": "gitleaks",
            "message": "Gitleaks scan completed",
            "data": document
        }), 200

    except subprocess.CalledProcessError:
        return jsonify({
            "status": "error",
            "tool": "gitleaks",
            "message": "Failed to clone or scan the repository",
            "data": None
        }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "tool": "gitleaks",
            "message": str(e),
            "data": None
        }), 500