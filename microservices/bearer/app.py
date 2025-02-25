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
        
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)

        #os.chdir(repo_path)

        # Run Bearer scan
        result = subprocess.run(
            ['bearer', 'scan', '.', '--exit-code', '0'],
            check=True,
            capture_output=True,
            text=True,
            cwd=repo_path
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
                f"{MONGODB_SERVICE_URL}/bearer/reports",
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
                f"{MONGODB_SERVICE_URL}/bearer/reports",
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
        stderr_message = e.stderr.strip() if e.stderr else "No error message available"
        return jsonify({
        "status": "error",
        "tool": "bearer",
        "message": f"Subprocess error: {stderr_message}",
        "data": None
    }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "tool": "bearer",
            "message": f"An unexpected error occurred: {str(e)}",
            "data": None
        }), 500

@app.route('/Bearer/<repo_name>/final_results', methods=['GET'])
def bearer_final(repo_name):
    try:
        # Retrieve Bearer report from MongoDB
        response = requests.get(f"{MONGODB_SERVICE_URL}/bearer/reports/{repo_name}")
        
        if response.status_code == 200:
            response_data = response.json()
            report = response_data.get("report")  # Extract the "report" field
            
            if report:
                # Parse the JSON string in the "report" field
                report_data = json.loads(report)
                
                # Retrieve severity levels, defaulting to 0 if not found
                critical = report_data.get("critical", 0)
                high = report_data.get("high", 0)
                medium = report_data.get("medium", 0)
                low = report_data.get("low", 0)
                
                # Prepare the document for insertion
                document = {
                    "tool": "bearer",
                    "repo_name": repo_name,
                    "critical": critical,
                    "high": high,
                    "medium": medium,
                    "low": low
                }
                
                # Insert the results into the `final_results` collection
                insert_result = requests.post(f"{MONGODB_SERVICE_URL}/final_results/reports", json=document)
                
                if insert_result.status_code == 200:
                    return jsonify({"status": "success", "message": "Results stored successfully"}), 200
                else:
                    return jsonify({"status": "error", "message": "Failed to insert results into final_results"}), 500
            
            else:
                return jsonify({"status": "error", "message": "Report not found in the response"}), 404
        
        else:
            return jsonify({"status": "error", "message": f"Failed to retrieve Bearer report for '{repo_name}'"}), response.status_code
    
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Error decoding the JSON report from MongoDB"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5004)