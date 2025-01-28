import streamlit as st
import subprocess
import re
from dotenv import load_dotenv
import os 
import requests 
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import time
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState

load_dotenv()
NGINX_URL = os.getenv("NGINX_URL")

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")
UPDATE_DB_URL = os.getenv("UPDATE_DB_URL")
def main():
    st.set_page_config(
        page_title="CrimePoirot",
        layout="wide",
        initial_sidebar_state="auto",
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
        .stButton>button {
        width: 300px;  /* Set the button width */
        height: 50px;  /* Set the button height */
    }
        
        [data-testid="stSidebar"]{
        background-color: #212121;
        color: #333;
        font-family: 'Times New Roman', Times, serif;
        padding: 20px;
    }
        .stSidebar .stTextInput input {
            background-color: #424242;  /* Light cyan background */
            color: #eoeoeo;             /* Dark teal text */
            padding: 10px;              /* Add padding to input */
            border-radius: 5px;         /* Rounded corners */
            border: 2px solid #7F8C8D;  /* Dark teal border */
            font-family: 'Times New Roman', Times, serif;
    }
        .stSidebar .stTextInput label {
            font-size: 26px;  /* Adjust the font size for the label */
    }
        .stSidebar .stTextInput {
            font-size: 18px;  /* Adjust the font size for the input */
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
        st.markdown(
            """
            ### 🔑 **Key Features of CrimePoirot**

            - **Secrets Detection**: Utilizes **GitLeaks** to uncover exposed secrets and credentials in your repositories.
            - **Supply Chain Risk Assessment**: Employs **Guarddog** to identify potential risks in dependencies and supply chains.
            - **Dependency Vulnerability Scanning**: Leverages **Safety** to analyze and detect vulnerabilities in project dependencies.
            - **Sensitive Data Analysis**: Uses **Bearer** to scan codebases for sensitive data exposure, ensuring robust data security.

            ### 🚀 **How to Use CrimePoirot**

            1. **Enter the GitHub Repository URL**: Provide the URL of the repository you want to analyze.
            2. **Select the Tools to Run**: Choose from the available tools based on your specific needs.
            - The available tools are: **GitLeaks**, **Guarddog**, **Safety**, and **Bearer**.
            3. **Define Weights for Selected Tools**: Assign weights to each selected tool to customize the trust score calculation. 
            - Ensure the sum of all weights equals **1**.
            4. **Run the Analysis**: Click the button to analyze the repository and view the trust score along with detailed results.
            
            """
        )
        nodes = [StreamlitFlowNode(id='1', pos=(100,100), data={'content': 'Enter Github URL'}, node_type='input', source_position='right', draggable=False),
                    StreamlitFlowNode('2', (300,0), {'content': 'Select from available tools'}, 'default', 'bottom', 'left', draggable=False),
                    StreamlitFlowNode('3', (300, 200), {'content': 'Define the weights'}, 'default', 'right', 'top', draggable=False),
                    StreamlitFlowNode('4', (500, 100), {'content': 'Run analysis'}, 'default', 'right', 'left', draggable=False),
                    StreamlitFlowNode('5', (700, 100), {'content': 'Choose tab'},'default', 'right', 'left', draggable=False),
                    StreamlitFlowNode('6', (850,0), {'content': 'View Analyis report'}, 'default', 'bottom', 'bottom', draggable=False),
                    StreamlitFlowNode('7', (850,200), {'content': 'View CrimePoirot report'}, 'default', 'bottom', 'top', draggable=False)
]

        edges = [StreamlitFlowEdge('1-2', '1', '2', animated=True),
                    StreamlitFlowEdge('2-3', '2', '3', animated=True),
                    StreamlitFlowEdge('3-4', '3', '4', animated=True),
                    StreamlitFlowEdge('4-5', '4', '5', animated=True),
                    StreamlitFlowEdge('5-6', '5', '6', animated=True),
                    StreamlitFlowEdge('5-7', '5', '7', animated=True)]

        state = StreamlitFlowState(nodes, edges)

        updated_state = streamlit_flow('ret_val_flow',
                            state,
                            fit_view=True,
                            get_node_on_click=True,
                            get_edge_on_click=True)

        st.write(f"Clicked on: {updated_state.selected_id}")  
        


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
            weight = st.text_input(f"Enter {tool_name} weight:", placeholder=placeholder)
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

        is_all_selected = all(selected_tools.values())

        # Collect weights with dynamic placeholders
        if is_all_selected:
            with st.sidebar:
            # All tools selected: Use recommended placeholders
                gitleaks_weight = get_weight_input("Gitleaks", "Recommended: 0.3")
                if gitleaks_weight is not None:
                    weights["Gitleaks"] = gitleaks_weight

                guarddog_weight = get_weight_input("Guarddog", "Recommended: 0.1")
                if guarddog_weight is not None:
                    weights["Guarddog"] = guarddog_weight

                safety_weight = get_weight_input("Safety", "Recommended: 0.1")
                if safety_weight is not None:
                    weights["Safety"] = safety_weight

                bearer_critical_weight = get_weight_input("Bearer critical vulns", "Recommended: 0.2")
                if bearer_critical_weight is not None:
                    weights["Bearer - Critical"] = bearer_critical_weight

                bearer_high_weight = get_weight_input("Bearer high vulns", "Recommended: 0.15")
                if bearer_high_weight is not None:
                    weights["Bearer - High"] = bearer_high_weight

                bearer_medium_weight = get_weight_input("Bearer medium vulns", "Recommended: 0.1")
                if bearer_medium_weight is not None:
                    weights["Bearer - Medium"] = bearer_medium_weight

                bearer_low_weight = get_weight_input("Bearer low vulns", "Recommended: 0.05")
                if bearer_low_weight is not None:
                    weights["Bearer - Low"] = bearer_low_weight

        else:
            with st.sidebar:
                # Not all tools selected: Use "0-1" placeholder
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
            parameter_counts = {
                    "Gitleaks": {
                        "leaks": 0
                    },
                    "Guarddog": {
                        "malicious_indicators": 0  
                    },
                    "Safety": {
                        "vulns": 0
                    },
                    "Bearer": {
                        "critical": 0,
                        "high": 0,
                        "medium": 0,
                        "low": 0,
                    }
                }
            # API calls within a spinner
            with st.spinner("Running scripts... Please wait."):
                try:
                    # POST request to API Gateway for analysis
                    response = requests.post(f"{NGINX_URL}/analyze", json=payload)
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        st.success("Analysis Completed!")
                        tabs_success = st.tabs(["📄 View analysis report", "📈 View metrics"])
                        with tabs_success[0]:
                            st.json(result_data)
                            # Fetch additional results
                            tools_param = '&'.join([f'tools={tool}' for tool in payload["tools"]])
                            url = f"{NGINX_URL}/final_results/{repo_name}?{tools_param}"
                            final_results = requests.get(url)
                            
                            if final_results.status_code == 200:
                                st.success("Findings moved to final_results collection of DataBase.")
                            else:
                                st.error(f"Error fetching final results: {final_results.status_code}")
                                st.text(final_results.text)
                            percentiles = {}
                            # Fetch percentile data if needed
                            for tool in payload["tools"]:
                                percentile_response = requests.get(f"{NGINX_URL}/percentile/{tool}/{repo_name}")
                                if percentile_response.status_code == 200:
                                    data = percentile_response.json()
                                    if tool == "Gitleaks":
                                        parameter_counts["Gitleaks"]["leaks"] = data["leaks"]
                                        percentiles["Gitleaks"] = {
                                            "percentile": data["percentile"]
                                        }
                                    elif tool == "Guarddog":
                                        parameter_counts["Guarddog"]["malicious_indicators"] = data["Guarddog findings"]
                                        percentiles["Guarddog"] = {
                                            "percentile": data["percentile"]
                                        }
                                    elif tool == "Safety":
                                        parameter_counts["Safety"]["vulns"] = data["Safety findings"]
                                        percentiles["Safety"] = {
                                            "percentile": data["percentile"]
                                        }
                                    elif tool == "Bearer":
                                        parameter_counts["Bearer"]["critical"] = data["critical vulnerabilities"]
                                        parameter_counts["Bearer"]["high"] = data["high vulnerabilities"]
                                        parameter_counts["Bearer"]["medium"] = data["medium vulnerabilities"]
                                        parameter_counts["Bearer"]["low"] = data["low vulnerabilities"]
                                        percentiles["Bearer"] = {
                                            "critical_percentile": data["critical percentile"],
                                            "high_percentile": data["high percentile"],
                                            "low_percentile": data["low percentile"],
                                            "medium_percentile": data["medium percentile"]
                                        }
                                    st.write(f"Percentile for {tool}:")
                                    st.json(data)
                        with tabs_success[1]:        
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
                            def make_donut(trust_score, colors):
    # Define the green color scheme
                              # Lighter green for Trust, darker green for background
                                
                                # Create the Plotly figure
                                fig = go.Figure(go.Pie(
                                    values=[trust_score, 100 - trust_score],  # Trust and untrusted values
                                    labels=["Trust", "Untrusted"],  # Chart labels
                                    marker=dict(colors=colors),  # Apply the green colors
                                    hole=0.7,  # Create the donut shape
                                    direction="clockwise",  # Rotate clockwise
                                    textinfo="none",  # Hide percentage values on the chart
                                    showlegend=False  # Hide legend
                                ))
                                trust_score=round(trust_score,2)
                                # Add the trust score as a centered annotation
                                fig.add_annotation(
                                    text=f"<b>{trust_score}%</b>",  # Display the trust score
                                    font=dict(size=18, color='#ffffff'),  # Use the lighter green for text
                                    showarrow=False,
                                    x=0.5, y=0.5,  # Center the text
                                    xref="paper", yref="paper"
                                )
                                
                                # Update layout for better styling
                                fig.update_layout(
                                    width=400,  # Set chart width
                                    height=400,  # Set chart height
                                    margin=dict(t=10, b=10, l=10, r=10),  # Adjust margins
                                )
                                
                                return fig
                            if trust_score > 50:
                                colors = ['#1dda6d', '#12783D']
                            else:
                                colors = ['#E74C3C', '#781F16']
                            # Generate the donut chart
                            donut_chart = make_donut(trust_score,colors)

                            # Display the donut chart in a column
                            col1, col2 = st.columns(2)
                            with col1:
                                st.subheader("Trust Score")
                                st.plotly_chart(donut_chart, use_container_width=False)
        
                            alt.theme.enable("dark")

                            # Assuming parameter_counts is a dictionary with tool and parameter counts
                            labels = []
                            counts = []
                            tools = ["Gitleaks", "Guarddog", "Safety", "Bearer"]  # Just an example, replace with your tool names
                            for tool, params in parameter_counts.items():
                                for param, count in params.items():
                                    labels.append(f"{tool} - {param}")
                                    counts.append(count)

                            # Create a DataFrame similar to the fruits example
                            df = pd.DataFrame({"labels": labels, "counts": counts})

                            # Define custom colors for each tool/parameter label
                            color_domain = labels  # Use the unique labels from the dataset
                            color_range = ["skyblue", "lightgreen", "lightcoral", "gold", "lightpink", "lightyellow", "lightgray"]  # Example colors, repeat as needed

                            # Create the Altair chart
                            chart = (
                                alt.Chart(df)
                                .mark_bar()
                                .encode(
                                    x=alt.X("labels"),  # Sorting based on the count or alphabetically
                                    y=alt.Y("counts", scale=alt.Scale(domain=[0, max(df['counts'])])),  # Ensure y-axis starts at 0                                    color=alt.Color(
                                    color=alt.Color(
                                            "labels",
                                            scale=alt.Scale(
                                                domain=color_domain,
                                                range=color_range,
                                            ),
                                                legend=None
                                           ),
                                )
                                .properties(
                                    width=900,  # Set the chart width
                                    height=500  # Set the chart height
                                )
                            )
                            with col2: 
                                st.subheader("Parameter Counts by selected tools")
                                # Display the chart in Streamlit
                                st.altair_chart(chart, use_container_width=True)
                        
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
            In every new repository we decide to scan, we find the percentage of 100 scanned repositories which have values-findings smaller than those of the new repository.
            According to this percentile, after defining the corresponding weights, a trust score will be calculated.
            This score will help the owner/ developer to have a quick measure to check about how safe is the repository.\n\n
            """
        )
        

        st.markdown("""
            ### **Create Database Button**

            The **Create Database** button is designed to initialize and populate the CrimePoirot database. It performs the following tasks:

            1. **Report Initialization**: Delete existing report.csv and create a new one with the required headers. 
            2. **Data Ingestion**: Runs predefined repositories ( located in `/microservices/update_db/app.py`) analyses  and stores the results in their corresponding collections.
            3. **Percentile Recalculation**: Calculates percentiles for each tool based on the new set of metrics from the analyzed repositories.
            
            This feature is used for setting up the database for the first time or starting with a clean slate.

            ---

            ### **Update Database Button**

            The **Update Database** button is used to update the existing CrimePoirot database with new or modified repository data. It performs the following operations:

            1. **Repository Update**: Runs an analysis on a specified list of Python repositories located in `/microservices/update_db/app.py`.
            2. **CSV File Update**: Updates the `report.csv` file with the latest metrics from the analyzed repositories.
            3. **Percentile Recalculation**: Recalculates percentiles based on the updated metrics in the CSV file, ensuring accurate trust score computations.

            This feature is used for maintaining an up-to-date database and incorporating new repositories into the analysis without starting over.

            ---

            ### **Key Differences**
            | Feature              | Create Database                     | Update Database                       |
            |----------------------|-------------------------------------|---------------------------------------|
            | **Purpose**          | Create new report.csv  | Add to the existing report.csv new repository metrics |
            | **Use Case**         | First-time setup or complete reset   | Periodic updates or adding repositories |

            Both buttons are critical for managing the CrimePoirot database, ensuring flexibility and scalability in repository trustworthiness analysis.
            """)

        
        ############    KEIMENO GIA TO CREATE DATABASE
        col1, col2 = st.columns(2)
        with col1:
            update_db_button = st.button("Update DataBase")
            if update_db_button:
                with st.spinner("Updating DataBase...This will take some hours."):
                    try:
                        # Send POST request to the update_db service
                        response = requests.post(f"{NGINX_URL}/update_db")
                        
                        # Check if the request was successful
                        if response.status_code == 200:
                            result = response.json()
                            st.success("DataBase updated successfully.")
                            st.json(result)
                            try:
                                # Attempt to parse JSON response
                                print(response.json())  # This prints the JSON response from the API
                            except ValueError:
                                print("Response is not in JSON format")
                                print(response.text)  # Print raw content if it's not JSON
                        else:
                            st.error(f"Error updating DataBase: {response.status_code}")
                            st.text(response.text)

                    except requests.ConnectionError:
                        st.error("Error: Unable to connect to the API Gateway.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")
        
        create_db_button = st.button("Create DataBase")
        if create_db_button:
            with st.spinner("Creating DataBase...This will take some hours."):
                try:
                    # Send POST request to the update_db service
                    response = requests.post(f"{UPDATE_DB_URL}/create_db")
                    
                    # Check if the request was successful
                    if response.status_code == 200:
                        result = response.json()
                        st.success("DataBase created successfully.")
                        st.json(result)
                        try:
                            # Attempt to parse JSON response
                            print(response.json())  # This prints the JSON response from the API
                        except ValueError:
                            print("Response is not in JSON format")
                            print(response.text)  # Print raw content if it's not JSON
                        
                        logs_placeholder = st.empty()
                        
                        # Start a thread to fetch logs from multiple containers
                        logs_thread = threading.Thread(target=fetch_logs, args=(container_names, logs_placeholder))
                        logs_thread.daemon = True  # Ensure the thread will close when the app does
                        logs_thread.start()

                        st.text("Fetching logs...")

                    else:
                        st.error(f"Error creating DataBase: {response.status_code}")
                        st.text(response.text)

                except requests.ConnectionError:
                    st.error("Error: Unable to connect to the API Gateway.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        


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
            [CrimePoirot Repository](https://github.com/kosmits-ai/TheCrimePoirot)
            """
        )
    
    # Footer
    st.markdown(
        "<div class='footer'>© 2024 CrimePoirot - Built by Konstantinos Mitsionis</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

