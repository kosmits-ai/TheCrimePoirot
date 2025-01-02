from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from scipy.stats import percentileofscore
import pandas as pd
import json

app = Flask(__name__)

load_dotenv()

# Path to CSV file
csv_path = os.getenv("CSV_PATH", "/tmp/data.csv")

# MongoDB service URL
MONGODB_SERVICE_URL = os.getenv("MONGO_SERVICE_URL")


@app.route('/percentile/Gitleaks/<repo_name>', methods=['GET'])
def gitleaks_percentile(repo_name):
    try:
        # Load CSV data
        if not os.path.exists(csv_path):
            return jsonify({"error": f"CSV file not found at {csv_path}"}), 404
        
        data = pd.read_csv(csv_path)
        
        if 'Total Repo Leaks' not in data.columns:
            return jsonify({"error": "CSV file does not contain 'Total Repo Leaks' column"}), 404

        # Fetch gitleaks final results from MongoDB service
        response = requests.get(f"http://{MONGODB_SERVICE_URL}/final_results/gitleaks/{repo_name}")
        if response.status_code == 200:
            response_data = response.json()
            leaks = response_data.get("leaks")

            if leaks is None:
                return jsonify({"error": "'leaks' field is missing in the report"}), 404

            # Calculate the percentile
            percentile = percentileofscore(data['Total Repo Leaks'], leaks, kind='strict')

            return jsonify({
                "success": True,
                "message": "Successfully calculated gitleaks percentile.",
                "repo_name": repo_name,
                "leaks": leaks,
                "percentile": percentile
            }), 200
        else:
            return jsonify({"error": f"Could not fetch gitleaks data for repo '{repo_name}'"}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/percentile/Guarddog/<repo_name>', methods=['GET'])
def guarddog_percentile(repo_name):
    try:
        # Load CSV data
        if not os.path.exists(csv_path):
            return jsonify({"error": f"CSV file not found at {csv_path}"}), 404
        
        data = pd.read_csv(csv_path)
        
        # Ensure the necessary column exists
        if 'Guarddog findings' not in data.columns:
            return jsonify({"error": "CSV file does not contain 'Guarddog findings' column"}), 404

        # Fetch guarddog final results from MongoDB service
        response = requests.get(f"http://{MONGODB_SERVICE_URL}/final_results/guarddog/{repo_name}")
        if response.status_code == 200:
            response_data = response.json()
            
            # Get the 'Malicious indications' from the response
            results = response_data.get("malicious indications")  # Assuming leaks holds the number of malicious findings

            if results is None:
                return jsonify({"error": "'malicious indications' field is missing in the response"}), 404

            # Calculate the percentile
            percentile = percentileofscore(data['Guarddog findings'], results, kind='strict')

            return jsonify({
                "success": True,
                "message": "Successfully calculated guarddog percentile.",
                "repo_name": repo_name,
                "Guarddog findings": results,
                "percentile": percentile
            }), 200
        else:
            return jsonify({"error": f"Could not fetch guarddog data for repo '{repo_name}'"}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/percentile/Safety/<repo_name>', methods=['GET'])
def safety_percentile(repo_name):
    try:
        # Load CSV data
        if not os.path.exists(csv_path):
            return jsonify({"error": f"CSV file not found at {csv_path}"}), 404
        
        data = pd.read_csv(csv_path)
        
        # Ensure the necessary column exists
        if 'Safety findings' not in data.columns:
            return jsonify({"error": "CSV file does not contain 'Safety findings' column"}), 404

        response = requests.get(f"http://{MONGODB_SERVICE_URL}/final_results/safety/{repo_name}")
        if response.status_code == 200:
            response_data = response.json()
            
            # Get the 'Malicious indications' from the response
            vulnerabilities = response_data.get("vulnerabilities")  # Assuming leaks holds the number of malicious findings

            if vulnerabilities is None:
                return jsonify({"error": "'vulnerabilities' field is missing in the response"}), 404

            # Calculate the percentile
            percentile = percentileofscore(data['Safety findings'], vulnerabilities, kind='strict')

            return jsonify({
                "success": True,
                "message": "Successfully calculated safety percentile.",
                "repo_name": repo_name,
                "Safety findings": vulnerabilities,
                "percentile": percentile
            }), 200
        else:
            return jsonify({"error": f"Could not fetch safety data for repo '{repo_name}'"}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/percentile/Bearer/<repo_name>', methods=['GET'])
def bearer_percentile(repo_name):
    try:
        # Load CSV data
        if not os.path.exists(csv_path):
            return jsonify({"error": f"CSV file not found at {csv_path}"}), 404
        
        data = pd.read_csv(csv_path)
        
        # List of necessary columns
        required_columns = ['Critical Vulns', 'High Vulns', 'Medium Vulns', 'Low Vulns']

        # Check if all necessary columns are present in the CSV data
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            return jsonify({"error": f"CSV file is missing the following columns: {', '.join(missing_columns)}"}), 404
        
        # Fetch the Bearer results from MongoDB
        response = requests.get(f"http://{MONGODB_SERVICE_URL}/final_results/bearer/{repo_name}")
        if response.status_code == 200:
            response_data = response.json()

            # Extract vulnerability data from the response
            critical_vulnerabilities = response_data.get("critical vulnerabilities")
            high_vulnerabilities = response_data.get("high vulnerabilities")
            medium_vulnerabilities = response_data.get("medium vulnerabilities")
            low_vulnerabilities = response_data.get("low vulnerabilities")

            # If any vulnerability data is missing, return an error
            if None in [critical_vulnerabilities, high_vulnerabilities, medium_vulnerabilities, low_vulnerabilities]:
                return jsonify({"error": "One or more vulnerability fields are missing in the Bearer results"}), 404

            # Calculate the percentiles for each vulnerability category
            critical_percentile = percentileofscore(data['Critical Vulns'], critical_vulnerabilities, kind='strict')
            high_percentile = percentileofscore(data['High Vulns'], high_vulnerabilities, kind='strict')
            medium_percentile = percentileofscore(data['Medium Vulns'], medium_vulnerabilities, kind='strict')
            low_percentile = percentileofscore(data['Low Vulns'], low_vulnerabilities, kind='strict')

            return jsonify({
                "success": True,
                "message": "Successfully calculated Bearer percentiles.",
                "repo_name": repo_name,
                "critical vulnerabilities": critical_vulnerabilities,
                "critical percentile": critical_percentile,
                "high vulnerabilities": high_vulnerabilities,
                "high percentile": high_percentile,
                "medium vulnerabilities": medium_vulnerabilities,
                "medium percentile": medium_percentile,
                "low vulnerabilities": low_vulnerabilities,
                "low percentile": low_percentile,
            }), 200
        else:
            return jsonify({"error": f"Could not fetch Bearer data for repo '{repo_name}'"}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5005)