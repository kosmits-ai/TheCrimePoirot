from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


# MongoDB URI (get this from your MongoDB Atlas account)
MONGO_URI = os.getenv("MONGO_URL") 

# Create a MongoDB client and database
client = MongoClient(MONGO_URI)
db = client["DiplomaThesis"]  # Database name


@app.route('/<tool_reports>/reports', methods=['POST'])
def insert_report(tool_reports):
    try:
        collection = db[tool_reports]
        data = request.json  # Get the data from the incoming request
        result = collection.insert_one(data)  # Insert data into MongoDB
        return jsonify({"status": "success", "message": "Document inserted", "id": str(result.inserted_id)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/<tool_reports>/reports/<repo_name>', methods=['GET'])
def get_report(tool_reports, repo_name):
    try:
        collection = db[tool_reports]
        report = collection.find_one({"repo_name": repo_name})  # Find report by repo_name
        if report:
            return jsonify({"status": "success", "report": dumps(report)}), 200  # Return the report in JSON format
        else:
            return jsonify({"status": "error", "message": "Report not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/<tool_reports>/reports', methods=['GET'])
def get_all_reports(tool_reports):
    try:
        collection = db[tool_reports]
        reports = collection.find()  # Retrieve all reports from the collection
        return jsonify({"status": "success", "reports": dumps(reports)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/<tool_reports>/reports/<repo_name>', methods=['PUT'])
def update_report(tool_reports,repo_name):
    try:
        collection = db[tool_reports]
        data = request.json  # Get the data from the incoming request
        result = collection.update_one({"repo_name": repo_name}, {"$set": data})  # Update the report
        if result.matched_count > 0:
            return jsonify({"status": "success", "message": "Document updated"}), 200
        else:
            return jsonify({"status": "error", "message": "Report not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/<tool_reports>/reports/<repo_name>', methods=['DELETE'])
def delete_report(tool_reports, repo_name):
    try:
        collection = db[tool_reports]
        result = collection.delete_one({"repo_name": repo_name})  # Delete the report by repo_name
        if result.deleted_count > 0:
            return jsonify({"status": "success", "message": "Document deleted"}), 200
        else:
            return jsonify({"status": "error", "message": "Report not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
@app.route('/final_results/gitleaks/<repo_name>', methods=['GET'])
def get_gitleaks_results(repo_name):
    try:
        collection = db['final_results']  # Access the correct collection
        result = collection.find_one({"repo_name": repo_name, "tool": "gitleaks"})  # Find the report for the given repo and tool
        
        if result:  # Check if a result was found
            # Directly extract the relevant fields instead of a non-existent 'report' field
            leaks = result.get("leaks")  # Extract the leaks field
            if leaks is not None:  # Check if leaks exists
                return jsonify({"status": "success", "repo_name": repo_name, "tool": "gitleaks", "leaks": leaks}), 200  # Return the result
            else:
                return jsonify({"status": "error", "message": "'leaks' field not found in the result"}), 404
        else:
            return jsonify({"status": "error", "message": "Report not found for the given repo and tool"}), 404
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/final_results/guarddog/<repo_name>', methods=['GET'])
def get_guarddog_results(repo_name):
    try:
        collection = db['final_results']  # Access the correct collection
        result = collection.find_one({"repo_name": repo_name, "tool": "guarddog"})  # Find the report for the given repo and tool
        
        if result:  # Check if a result was found
            # Directly extract the relevant fields instead of a non-existent 'report' field
            malicious_indications = result.get("malicious_indications")  # Extract the leaks field
            if malicious_indications is not None:  # Check if leaks exists
                return jsonify({"status": "success", "repo_name": repo_name, "tool": "guarddog", "malicious indications": malicious_indications}), 200  # Return the result
            else:
                return jsonify({"status": "error", "message": "'Malicious indications' field not found in the result"}), 404
        else:
            return jsonify({"status": "error", "message": "Report not found for the given repo and tool"}), 404
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/final_results/safety/<repo_name>', methods=['GET'])
def get_safety_results(repo_name):
    try:
        collection = db['final_results']  # Access the correct collection
        result = collection.find_one({"repo_name": repo_name, "tool": "safety"})  # Find the report for the given repo and tool
        
        if result:  # Check if a result was found
            # Directly extract the relevant fields instead of a non-existent 'report' field
            vulnerabilities = result.get("vulnerabilities")  # Extract the leaks field
            if vulnerabilities is not None:  # Check if leaks exists
                return jsonify({"status": "success", "repo_name": repo_name, "tool": "guarddog", "vulnerabilities": vulnerabilities}), 200  # Return the result
            else:
                return jsonify({"status": "error", "message": "'vulnerabilities' field not found in the result"}), 404
        else:
            return jsonify({"status": "error", "message": "Report not found for the given repo and tool"}), 404
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/final_results/bearer/<repo_name>', methods=['GET'])
def get_bearer_results(repo_name):
    try:
        collection = db['final_results']  # Access the correct collection
        result = collection.find_one({"repo_name": repo_name, "tool": "bearer"})  # Find the report for the given repo and tool
        
        if result:  # Check if a result was found
            # Extract the relevant fields
            critical = result.get("critical")
            high = result.get("high")
            medium = result.get("medium")
            low = result.get("low")
            
            # Check for missing fields
            missing_fields = []
            if critical is None: missing_fields.append("critical")
            if high is None: missing_fields.append("high")
            if medium is None: missing_fields.append("medium")
            if low is None: missing_fields.append("low")
            
            if missing_fields:
                return jsonify({"status": "error", "message": f"Missing values for: {', '.join(missing_fields)}"}), 404

            return jsonify({
                "status": "success",
                "repo_name": repo_name,
                "tool": "bearer",
                "critical vulnerabilities": critical,
                "high vulnerabilities": high,
                "medium vulnerabilities": medium,
                "low vulnerabilities": low
            }), 200
        else:
            return jsonify({"status": "error", "message": "Report not found for the given repo and tool"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)  # Run on a different port if needed
