from flask import Flask, request, jsonify
import subprocess
import requests
import os
import shutil
import json 
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
MONGODB_SERVICE_URL = os.getenv("MONGO_SERVICE_URL")
BASE_DIR = os.getenv("BASE_DIR", "/tmp/repos") # (ensure this exists and is writable)


@app.route('/analyze', methods=['POST'])
def analyze_repo():
    """
    Analyze a repository using Guarddog and store the results in MongoDB.
    """
    try:
        # Get the repository URL from the request
        repo_url = request.json.get("repo_url")
        if not repo_url:
            return jsonify({"status": "error", "tool": "guarddog", "message": "Repository URL is required", "data": None}), 400

    
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join(BASE_DIR, repo_name)
        requirements_path = os.path.join(repo_path, 'requirements.txt')

        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)

        if not os.path.exists(requirements_path):
            return jsonify({"status": "error", "tool": "guarddog", "message": "requirements.txt not found in the repository", "data": None}), 404

        process = subprocess.run(
            [
                "python", "-m", "guarddog", "pypi", "verify",
                "-x", "repository_integrity_mismatch",
                requirements_path,
                "--output-format", "sarif"
            ],
            capture_output=True,
            text=True
        )
        if process.returncode != 0:
            return jsonify({"status": "error", "tool": "guarddog", "message": process.stderr.strip(), "data": None}), 500

        try:
            sarif_data = json.loads(process.stdout.strip()) #make output in json format.
            runs = sarif_data.get("runs", []) if isinstance(sarif_data, dict) else []
            if not runs:
                return jsonify({"status": "success", "tool": "guarddog", "message": "No suspicious findings", "data": []}), 200

            # Aggregate results
            results = []
            for run in runs:
                results.extend(run.get("results", []))

            cleaned_results = []
            for result in results:      #get specific information from results
                rule_id = result.get("ruleId", "N/A")
                message_text = result.get("message", {}).get("text", "").strip()
                unique_lines = list(dict.fromkeys(message_text.split("\n")))  # Remove duplicates
                cleaned_results.append({
                    "rule_id": rule_id,
                    "output_text": "\n".join(unique_lines)
                })

            document = {
                "repo_name": repo_name,
                "results": cleaned_results if cleaned_results else "No suspicious findings"
            }
        except json.JSONDecodeError as e:
            return jsonify({"status": "error", "tool": "guarddog", "message": f"Invalid SARIF JSON: {str(e)}", "data": None}), 500

        # Store results in MongoDB
        response = requests.post(
            f"http://{MONGODB_SERVICE_URL}/guarddog/reports",
            json=document
        )
        if response.status_code != 200:
            return jsonify({"status": "error", "tool": "guarddog", "message": "Failed to store results in MongoDB", "data": None}), 500

        return jsonify({"status": "success", "tool": "guarddog", "message": "Analysis complete", "data": document}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "tool": "guarddog", "message": f"Subprocess error: {e}", "data": None}), 500
    except Exception as e:
        return jsonify({"status": "error", "tool": "guarddog", "message": str(e), "data": None}), 500