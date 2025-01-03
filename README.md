# TheCrimePoirot
## **Introduction**
My work for my diploma thesis _Detection of Vulnerabilities/Malware in Open Source Platforms with Python_.
I used four open source projects from Github:
1. **GitLeaks** : Secret Detection like passwords, API keys, and tokens in git repos, files
2. **GuardDog** : Identification of malicious PyPI and npm packages or Go modules
3. **Safety** : Python dependency vulnerability scanner
4. **Bearer** : Static application security testing (SAST) tool that scans the source code and analyzes the data flows to discover, filter and prioritize security and privacy risks.

## **Main idea behind this project:**
The main idea behind this project was building a tool that can check for various parameters which affect the security trust for a specific repository. After evaluating the findings of Gitleaks, GuardDog, Safety, Bearer for 100 random repositories, we build a csv report which contains the values-findings for all security parameters. In every new repository we decide to scan,we find the percentage of 100 scanned repositories which have values-findings smaller than those of the new repository. According to this percentile, after defining the corresponding weights, a trust score will be calculated. This score will help the owner/ developer to have a quick measure to check about how safe is the repository.

## **How To Use:**
What steps to follow in order to use TheCrimePoirot:
1. `git clone <repo url>`
2. Create venv in project root directory: `python3 -m venv venv`
3. In **venv**: `pip install -r requirements.txt`
4. In root directory: `git clone https://github.com/gitleaks/gitleaks`
5. If you have Go installed: `cd gitleaks`,  `make build`
6.  Authentication for **Safety** :
  - `safety auth`
7. Install **Bearer** package:
  - ```
    sudo apt-get install apt-transport-https
    echo "deb [trusted=yes] https://apt.fury.io/bearer/ /" | sudo tee -a /etc/apt/sources.list.d/fury.list
    sudo apt-get update
    sudo apt-get install bearer
    
## **Run the Scripts:**
1. `./start_services.sh`
2. Cd to api_gateway: `python app.py`
3. In new terminal:
- `cd microservices/frontend`
- `streamlit run app.py` 
After following this instructions, frontend will be up in a localhost.

###  How to scan repo in frontend:
1. Navigate to Run Scripts tab.
2. Enter a GitHub repository URL.
3. Select which tools you want to run.
4. Based on your choice, you have to define the according weights.
5. Available tools are: Gitleaks, Guarddog, Safety, Bearer.
6. The sum of the corresponding weights must be equal to 1.

