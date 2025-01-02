from flask import Flask, request, jsonify
import os
import subprocess
import shutil
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
import json
import re


load_dotenv()

app = Flask(__name__)

MONGODB_SERVICE_URL = os.getenv("MONGO_SERVICE_URL")
BASE_DIR = os.getenv("BASE_DIR", "/tmp")  # Default to /tmp if not set


@app.route('/analyze', methods=['POST'])
def run_bearer():
    
    repo_url = request.json.get("repo_url")
    if not repo_url:
        return jsonify({"status": "error", "tool": "bearer", "message": "Repository URL is required", "data": None}), 400

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(BASE_DIR, repo_name)
    
    try:
        # Clone the repository
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)  # Remove existing repository  in order to get the latest commit every time.
        

        os.chdir(repo_path)

        # Run Bearer scan
        result = subprocess.run(
            ['bearer', 'scan', '.', '--exit-code', '0'],
            check=True,
            capture_output=True,
            text=True
        )

        print("Scan completed successfully.")
        print(result.stdout)

        # Parse summary
        summary_pattern = re.compile(r"CRITICAL:\s(\d+).*HIGH:\s(\d+).*MEDIUM:\s(\d+).*LOW:\s(\d+).*WARNING:\s(\d+)", re.DOTALL)
        summary_match = summary_pattern.search(result.stdout)

        vulnerabilities = []
        # Extract vulnerability descriptions
        description_pattern = re.compile(r"(LOW|MEDIUM|HIGH|CRITICAL): (.+?)\nFile:\s([^\n]+)\s*", re.DOTALL)
        for match in description_pattern.finditer(result.stdout):
            severity = match.group(1)
            description = match.group(2).strip()
            file = match.group(3).strip()
            vulnerabilities.append({"severity": severity, "description": description, "file": file})

        if summary_match:
            # Parse the counts
            critical = int(summary_match.group(1))
            high = int(summary_match.group(2))
            medium = int(summary_match.group(3))
            low = int(summary_match.group(4))
            warning = int(summary_match.group(5))

            scan_summary = {
                "repo_name": repo_name,
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "warning": warning,
                "vulnerabilities": vulnerabilities
            }

            # Store results in MongoDB
            response = requests.post(
                f"http://{MONGODB_SERVICE_URL}/bearer/insert",
                json=scan_summary
            )

            if response.status_code != 200:
                return jsonify({"status": "error", "tool": "bearer", "message": "Failed to store results in MongoDB", "data": None}), 500

            return jsonify({
                "status": "success",
                "tool": "bearer",
                "message": "Analysis complete",
                "data": scan_summary
            }), 200

        else:  #No vulnerabilites found
            print("No summary found in the output.")
            scan_summary = {
                "repo_name": repo_name,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "warning": 0,
                "vulnerabilities": 0
            }
            response = requests.post(
                f"http://{MONGODB_SERVICE_URL}/bearer/insert",
                json=scan_summary
            )

            if response.status_code != 200:
                return jsonify({"status": "error", "tool": "bearer", "message": "Failed to store results in MongoDB", "data": None}), 500

            return jsonify({
                "status": "success",
                "tool": "bearer",
                "message": "Analysis complete",
                "data": scan_summary
            }), 200
            

    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "tool": "bearer",
            "message": f"Subprocess error: {e.stderr.strip()}",
            "data": None
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "tool": "bearer",
            "message": f"An unexpected error occurred: {str(e)}",
            "data": None
        }), 500

    