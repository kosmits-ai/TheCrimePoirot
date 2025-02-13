import anthropic
from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
import json
from dotenv import load_dotenv
import os 
from bson import json_util

app = Flask(__name__)
load_dotenv()
# MongoDB URI (get this from your MongoDB Atlas account)
MONGO_URI = os.getenv("MONGO_URL") 
client = MongoClient(MONGO_URI)
db = client["DiplomaThesis"]  # Database name

def get_analysis(repo_name, tools):
    results = {}
    for tool in tools:
        tool_results = {
            tool :list(db[tool].find({"repo_name": repo_name} ))
        }
        if tool_results:
            results[tool] = tool_results

    return results
from bson import ObjectId

def serialize_mongo_data(data):
    """Recursively convert MongoDB data types to serializable formats."""
    if isinstance(data, list):
        return [serialize_mongo_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_mongo_data(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)  # Convert ObjectId to string
    else:
        return data  # Return other types as is

def prepare_findings_claude(results, tools):
    # Serialize MongoDB results before sending to Claude API
    serialized_results = serialize_mongo_data(results)
    
    json_data = json.dumps(serialized_results, indent=2)
    
    prompt = f"""You are one of the best security analyzers for Python Github repositories.
    The data are results from scanned github repositories by github open source tools Gitleaks, Guarddog, Safety, Bearer.
    In the provided data, findings are organised according to the tool name. Analyze those findings, categorize the dangers and recommend possible fixes for the client.
    Findings data:
    {json_data}
    Selected tools:
    {tools}
    Please do the following:
    1. Analyze the findings for every available tool in plain text.
    2. Recommend possible fixes for every security problem.
    3. Based on the dangers, categorize the repository to SAFE, NEUTRAL SECURITY, or DANGEROUS.
    """
    return prompt


def get_claude_response(prompt):
    client = anthropic.Anthropic(
        api_key=os.getenv("CLAUDE_API_KEY")
    )
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Check if the response is valid and print status or errors
        if response is None:
            print("Response is null or empty.")
            return "Error: No response from Claude API."

        # If we got a response, check for the text content
        print("Response:", response)  # This will show the full response for debugging
        
        return response.content[0].text
    
    except Exception as e:
        print("Error while calling the Claude API:", str(e))
        return f"Error: {str(e)}"

    

@app.route('/scan', methods=['POST'])
def scan_claude():
    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        repo_url = data.get('repo_url')
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        tools = data.get('tools')
        
        if not repo_name or not tools:
            return jsonify({"error": "Repository name and tools are required"}), 400
        
        # Get analysis results
        results={}
        results = get_analysis(repo_name, tools)
        if not results:
            return jsonify({"error": "No results found"}), 404
        
        # Prepare and get Claude's response
        prompt = prepare_findings_claude(results,tools)
        comment = get_claude_response(prompt)
        
        return jsonify({"output": comment}), 200
    
    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5014)
