from flask import Flask, jsonify, request
import requests

app = Flask(__name__)


SERVICES = json.loads(os.getenv("SERVICES"))

PERCENTILE_SERVICE = os.getenv("PERCENTILE_SERVICE")

@app.route('/analyze', methods=['POST'])
def analyze():
    """Route to analyze a repository using some/all tools."""
    data = request.get_json()
    repo_url = data.get("repo_url")
    tools = data.get("tools")
    if not repo_url:
        return jsonify({
            "status": "error",
            "message": "Repository URL is required",
            "data": None
        }), 400
    if not tools:
        return jsonify({
            "status": "error",
            "message": "Tools are required",
            "data": None
        }), 400

    results = {}

    # Iterate through the tools and call their respective microservices
    for tool in tools:
        service_url = SERVICES.get(tool)
        if service_url:
            try:
                response = requests.post(f"{service_url}/analyze", json={"repo_url": repo_url})
                
                # Parse response from each tool's service
                if response.status_code == 200:
                    results[tool] = {
                        "status": "success",
                        "data": response.json()
                    }
                else:
                    results[tool] = {
                        "status": "error",
                        "message": f"{tool} service returned an error",
                        "status_code": response.status_code,
                        "response": response.text
                    }
            except requests.ConnectionError:
                results[tool] = {
                    "status": "error",
                    "message": f"Could not connect to the {tool} service"
                }
            except Exception as e:
                results[tool] = {
                    "status": "error",
                    "message": f"Unexpected error occurred with {tool} service",
                    "exception": str(e)
                }

    # Return consolidated results
    return jsonify({
        "status": "complete",
        "repo_url": repo_url,
        "results": results
    }), 200


@app.route('/final_results/<repo_name>', methods=['GET'])
def final_results(repo_name):
    """Route to get and move final results to MongoDB for a specific repository."""
    selected_tools = request.args.getlist('tools')
    if not selected_tools:
        return jsonify({"error": "No tools selected"}), 400
    
    results = {}

    # Iterate through the tools and move the results to the final_results collection
    for tool in selected_tools:
        service_url = SERVICES.get(tool)
        
        if not service_url:
            results[tool] = {
                "status": f"Tool {tool} is not recognized."
            }
            continue
        try:
            # Send a request to the tool service to move the results to the DB
            response = requests.get(f"{service_url}/{tool}/{repo_name}/final_results")
            
            if response.status_code == 200:
                results[tool] = {
                    "status": f"Success in moving results to DB final_results for {tool}"
                }
            else:
                results[tool] = {
                    "status": f"Error in moving results to DB final_results for {tool}",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except requests.ConnectionError:
            results[tool] = {
                "status": "error",
                "message": f"Could not connect to the {tool} service"
            }
        except Exception as e:
            results[tool] = {
                "status": "error",
                "message": f"Unexpected error occurred with {tool} service",
                "exception": str(e)
            }

    # Return the final results summary
    return jsonify({
        "status": "complete",
        "repo_name": repo_name,
        "results": results
    }), 200



@app.route('/percentile/<tool>/<repo_name>', methods=['GET'])
def get_percentile(tool, repo_name):
    """Fetch the percentile for a specific tool and repository."""
    if tool not in SERVICES:
        return jsonify({"error": f"Tool '{tool}' not found"}), 404

    try:
        # Call the percentile service
        response = requests.get(f"{PERCENTILE_SERVICE}/percentile/{tool}/{repo_name}")
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "error": f"Percentile service returned an error for tool '{tool}' and repo '{repo_name}'",
                "status_code": response.status_code,
                "response": response.text,
            }), response.status_code
    except requests.ConnectionError:
        return jsonify({"error": "Could not connect to the Percentile service"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    """Default 404 handler."""
    return jsonify({"error": "Route not found"}), 404




if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5007)


