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

'''
def authenticate_safety():
    try:
        print("Authenticating with Safety...")
        result = subprocess.run(['safety', 'auth'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Safety authentication failed: {result.stderr}")
        print("Successfully authenticated with Safety.")
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        raise

# Call authenticate_safety when the app starts
authenticate_safety()
'''
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
        
        subprocess.run(["git", "clone", repo_url, repo_path],capture_output=True, text=True, check=True)
        '''
        os.chdir(repo_path)
        print(f"Running Safety on {repo_path}...")
        '''
        safety_api_key = os.getenv("SAFETY_API_KEY")
        if not safety_api_key:
            raise EnvironmentError("SAFETY_API_KEY environment variable is not set.")

        result = subprocess.run(['safety', 'scan','--key', safety_api_key], cwd=repo_path, capture_output=True, text=True)
        print("Safety stdout:", result.stdout)
        print("Safety stderr:", result.stderr)



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
            f"{MONGODB_SERVICE_URL}/safety/reports",
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


@app.route('/Safety/<repo_name>/final_results', methods=['GET'])
def safety_final(repo_name):
    try:
        # Retrieve Safety report from MongoDB
        response = requests.get(f"{MONGODB_SERVICE_URL}/safety/reports/{repo_name}")
        
        if response.status_code == 200:
            response_data = response.json()
            report = response_data.get("report")  # Extract the "report" field
            
            if report:
                # Parse the JSON string in the "report" field
                report_data = json.loads(report)
                vulnerabilities = report_data.get("vulnerabilities", [])  # Defaults to an empty list
                
                # Create the final results document
                document = {
                    "tool": "safety",
                    "repo_name": repo_name,
                    "vulnerabilities": len(vulnerabilities)  # Number of vulnerabilities
                }

                # Insert the summarized results into the `final_results` collection
                insert_result = requests.post(f"{MONGODB_SERVICE_URL}/final_results/reports", json=document)
                
                if insert_result.status_code == 200:
                    return jsonify({"status": "success", "message": "Results stored successfully"}), 200
                else:
                    return jsonify({"status": "error", "message": "Failed to insert results into final_results"}), 500
            
            else:
                return jsonify({"status": "error", "message": "Report not found in the response"}), 404
        
        else:
            return jsonify({"status": "error", "message": f"Failed to retrieve Safety report for '{repo_name}'"}), response.status_code
    
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Error decoding the JSON report from MongoDB"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5003)