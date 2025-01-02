import streamlit as st
import subprocess
import re
from dotenv import load_dotenv
import os 
import requests 

load_dotenv()

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")

def main():
    st.set_page_config(
        page_title="CrimePoirot",
        layout="centered",
        initial_sidebar_state="collapsed",
        page_icon="🔍"
    )
    
    # Header with Times New Roman font style
    st.markdown(
        """
        <style>
        body {
            font-family: 'Times New Roman', Times, serif;
        }

        .main-title {
            font-size: 2.5em;
            color: #3cd110;
            text-align: center;
        }
        .sub-title {
            font-size: 1.2em;
            color: #7F8C8D;
            text-align: center;
        }
        .footer {
            text-align: center;
            color: #95A5A6;
            font-size: 0.9em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div class='main-title'>CrimePoirot</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Your GitHub Repository Analyzer</div>", unsafe_allow_html=True)
    st.write("---")

    # Tabs for navigation
    tabs = st.tabs(["🏠 Home", "🛠️ Run Scripts","📊 DB CrimePoirot", "ℹ️ About"])
    
    # Home Tab
    with tabs[0]:
        st.subheader("Welcome to CrimePoirot!")
        st.markdown(
            """
            ### 🔑 Features
            - Detects secrets using **GitLeaks**
            - Identifies supply chain risks with **Guarddog**
            - Checks dependencies for vulnerabilities via **Safety**
            - Scans codebases for sensitive data with **Bearer**
            
            ### 🚀 How to use:
            1. Enter a GitHub repository URL.
            2. Select which tools you want to run.
            3. Based on your choice, you have to define the according weights.
            4. Available tools are: Gitleaks, Guarddog, Safety, Bearer.
            5. The sum of the corresponding weights must be equal to 1.
            
            """  
        )


    with tabs[1]:
        st.subheader("Analyze Your Repository")
        
        # Input for GitHub repository URL
        repo_url = st.text_input(
            "🔗 Enter GitHub Repository URL", 
            placeholder="https://github.com/username/repo.git"
        )
        
        # Tool selection checkboxes
        st.write("### Select Tools to Run:")
        selected_tools = {
            "Gitleaks": st.checkbox("Run GitLeaks"),
            "Guarddog": st.checkbox("Run Guarddog"),
            "Safety": st.checkbox("Run Safety"),
            "Bearer": st.checkbox("Run Bearer"),
        }
        
        # Initialize a dictionary to store the weight inputs
        weights = {}

        # Conditional display of weight inputs based on tool selection
        def get_weight_input(tool_name, placeholder):
            weight = st.text_input(f"Enter {tool_name} weight for trust score calculation", placeholder=placeholder)
            if weight:
                try:
                    weight = float(weight)
                    if 0 <= weight <= 1:
                        return weight
                    else:
                        st.error(f"⚠️ {tool_name} weight must be between 0 and 1.")
                except ValueError:
                    st.error(f"⚠️ Please enter a valid numeric value for {tool_name} weight.")
            return None

        # Collect weights
        if selected_tools["Gitleaks"]:
            gitleaks_weight = get_weight_input("Gitleaks", "0-1")
            if gitleaks_weight is not None:
                weights["Gitleaks"] = gitleaks_weight

        if selected_tools["Guarddog"]:
            guarddog_weight = get_weight_input("Guarddog", "0-1")
            if guarddog_weight is not None:
                weights["Guarddog"] = guarddog_weight

        if selected_tools["Safety"]:
            safety_weight = get_weight_input("Safety", "0-1")
            if safety_weight is not None:
                weights["Safety"] = safety_weight

        if selected_tools["Bearer"]:
            bearer_critical_weight = get_weight_input("Bearer critical vulnerabilities", "0-1")
            if bearer_critical_weight is not None:
                weights["Bearer - Critical"] = bearer_critical_weight

            bearer_high_weight = get_weight_input("Bearer high vulnerabilities", "0-1")
            if bearer_high_weight is not None:
                weights["Bearer - High"] = bearer_high_weight

            bearer_medium_weight = get_weight_input("Bearer medium vulnerabilities", "0-1")
            if bearer_medium_weight is not None:
                weights["Bearer - Medium"] = bearer_medium_weight

            bearer_low_weight = get_weight_input("Bearer low vulnerabilities", "0-1")
            if bearer_low_weight is not None:
                weights["Bearer - Low"] = bearer_low_weight

        # Check if the sum of the weights is 1
        total_weight = sum(weights.values())

        # Error if total weight does not equal 1
        if total_weight != 1:
            st.warning(f"⚠️Please make sure the sum of all weights is equal to 1.")
            run_analysis_disabled = True  # Disable the "Run Analysis" button
        else:
            st.success("Weights are valid. The sum of weights is 1.")
            run_analysis_disabled = False  # Enable the "Run Analysis" button

        # Initialize session state
        if "analysis_successful" not in st.session_state:
            st.session_state.analysis_successful = False
        
        # Run Analysis Button
        run_analysis_button = st.button("Run Analysis", disabled=run_analysis_disabled)

        if run_analysis_button:
            
            # Validate GitHub repository URL
            if not re.match(r"https://github\.com/[\w-]+/[\w-]+(\.git)?", repo_url):
                st.error("⚠️ Please enter a valid GitHub repository URL.")
                
            
            # Check if at least one tool is selected
            if not any(selected_tools.values()):
                st.warning("Please select at least one tool to run.")
                
            
            # Prepare API payload
            payload = {
                "repo_url": repo_url,
                "tools": [tool for tool, selected in selected_tools.items() if selected],
            }
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            
            # API calls within a spinner
            with st.spinner("Running scripts... Please wait."):
                try:
                    # POST request to API Gateway for analysis
                    response = requests.post(f"{API_GATEWAY_URL}/analyze", json=payload)
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        st.success("Analysis Completed!")
                        st.json(result_data)
                        # Fetch additional results
                        tools_param = '&'.join([f'tools={tool}' for tool in payload["tools"]])
                        url = f"{API_GATEWAY_URL}/final_results/{repo_name}?{tools_param}"
                        final_results = requests.get(url)
                        
                        if final_results.status_code == 200:
                            st.success("Findings moved to final_results collection of DataBase.")
                        else:
                            st.error(f"Error fetching final results: {final_results.status_code}")
                            st.text(final_results.text)
                        percentiles = {}
                        # Fetch percentile data if needed
                        for tool in payload["tools"]:
                            percentile_response = requests.get(f"{API_GATEWAY_URL}/percentile/{tool}/{repo_name}")
                            if percentile_response.status_code == 200:
                                data = percentile_response.json()
                                if tool == "Gitleaks":
                                    percentiles["Gitleaks"] = {
                                        "percentile": data["percentile"]
                                    }
                                elif tool == "Guarddog":
                                    percentiles["Guarddog"] = {
                                        "percentile": data["percentile"]
                                    }
                                elif tool == "Safety":
                                    percentiles["Safety"] = {
                                        "percentile": data["percentile"]
                                    }
                                elif tool == "Bearer":
                                    percentiles["Bearer"] = {
                                        "critical_percentile": data["critical percentile"],
                                        "high_percentile": data["high percentile"],
                                        "low_percentile": data["low percentile"],
                                        "medium_percentile": data["medium percentile"]
                                    }
                                st.write(f"Percentile for {tool}:")
                                st.json(data)
                        trust_score = 0
                        score = 0
                        for tool, weight in weights.items():
                            if tool == "Gitleaks" and "Gitleaks" in percentiles:
                                gitleaks_percentile = percentiles["Gitleaks"]["percentile"]
                                score += weight * gitleaks_percentile  # Multiply weight by percentile for Gitleaks
                                       
                            elif tool == "Guarddog" and "Guarddog" in percentiles:
                                guarddog_percentile = percentiles["Guarddog"]["percentile"]
                                score += weight * guarddog_percentile  # Multiply weight by percentile for Guarddog     
                            elif tool == "Safety" and "Safety" in percentiles:
                                safety_percentile = percentiles["Safety"]["percentile"]
                                score += weight * safety_percentile  # Multiply weight by percentile for Safety   
                            elif tool == "Bearer - Critical" and "Bearer" in percentiles:
                                bearer_percentile = percentiles["Bearer"]["critical_percentile"]
                                score += weight * bearer_percentile  # Multiply weight by critical percentile for Bearer
                                      
                            elif tool == "Bearer - High" and "Bearer" in percentiles:
                                bearer_percentile = percentiles["Bearer"]["high_percentile"]
                                score += weight * bearer_percentile  # Multiply weight by high percentile for Bearer
                                        
                                        
                            elif tool == "Bearer - Medium" and "Bearer" in percentiles:
                                bearer_percentile = percentiles["Bearer"]["medium_percentile"]
                                score += weight * bearer_percentile  # Multiply weight by medium percentile for Bearer
                                        
                                        
                            elif tool == "Bearer - Low" and "Bearer" in percentiles:
                                bearer_percentile = percentiles["Bearer"]["low_percentile"]
                                score += weight * bearer_percentile  # Multiply weight by low percentile for Bearer
                                        
      
                            else:
                                st.warning(f"Percentile data for {tool} could not be retrieved.")
                                
                        trust_score = 100 - score  # Subtract total weighted score from 100
                        st.success(f"Calculated Trust Score: {trust_score}")
                    else:
                        st.error(f"API Gateway Error: {response.status_code}")
                        st.text(response.text)
                
                except requests.ConnectionError:
                    st.error("Error: Unable to connect to the API Gateway.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")


                    
    with tabs[2]:
        st.subheader("About CrimePoirot DataBase")
        st.markdown(
            """
            The main idea behind this project was building a tool that can check for various parameters which affect the security trust for a specific repository.
            After evaluating the findings of Gitleaks, GuardDog, Safety, Bearer for 100 random repositories, we build a csv report which contains the values-findings for all security parameters.
            In every new repository we decide to scan,we find the percentage of 100 scanned repositories which have values-findings smaller than those of the new repository.
            According to this percentile, after defining the corresponding weights, a trust score will be calculated.
            This score will help the owner/ developer to have a quick measure to check about how safe is the repository.\n\n
            """
        )
        workflow_path = os.getenv("WORKFLOW_IMAGE_PATH")
        histograms_path = os.getenv("HISTOGRAMS_IMAGE_PATH")
        st.markdown("##### Creation workflow of DataBase:")
        st.image(workflow_path,use_container_width= True)
        st.markdown("##### Histograms of DataBase Features:")
        st.image(histograms_path, use_container_width=True)


    # About Tab
    with tabs[3]:
        st.subheader("About CrimePoirot")
        st.markdown(
            """
            ### 🔍 What is CrimePoirot?
            CrimePoirot is a tool designed for GitHub repository analysis. It integrates multiple open-source security tools to detect vulnerabilities and calculate a repository trust score.
            
            ### ⚙️ Tools Used:
            - **GitLeaks**: Detects secrets in codebases.
            - **Guarddog**: Identifies supply chain risks in Python dependencies.
            - **Safety**: Checks for known vulnerabilities in dependencies.
            - **Bearer**: Scans for sensitive data exposure.

            ### 🛠️ Made With:
            - **Python**
            - **Streamlit** for UI
            - **MongoDB** for data storage

            ### 🤖 Project source code:
            [CrimePoirot Repository](https://github.com/kosmits-ai/CrimePoirot)
            """
        )
    
    # Footer
    st.markdown(
        "<div class='footer'>© 2024 CrimePoirot - Built by Konstantinos Mitsionis</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

