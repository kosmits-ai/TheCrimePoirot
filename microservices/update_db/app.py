from flask import Flask, jsonify, request
import requests
import json
import os
from dotenv import load_dotenv
import csv

repo_urls = {
    "Discord-Vanity-URL-Sniper": "https://github.com/kxndemir/Discord-Vanity-URL-Sniper.git",
    "dvpwa": "https://github.com/anxolerd/dvpwa.git",
    "vcfpy": "https://github.com/bihealth/vcfpy.git",
    "Telegram-SedenUserBot": "https://github.com/TeamDerUntergang/Telegram-SedenUserBot.git",
    "pandas_alive": "https://github.com/JackMcKew/pandas_alive.git",
    "content-engine": "https://github.com/groveco/content-engine.git",
    "TwinDiffusion": "https://github.com/0606zt/TwinDiffusion.git",
    "osintr": "https://github.com/bellyfat/osintr.git",
    "BRANDED-ROBOT": "https://github.com/WCGKING/BRANDED-ROBOT.git",
    "vaurien": "https://github.com/community-libs/vaurien.git",
    "trapster-community": "https://github.com/0xBallpoint/trapster-community.git",
    "xsrfprobe": "https://github.com/alex14324/xsrfprobe.git",
    "EveryoneNobel": "https://github.com/16131zzzzzzzz/EveryoneNobel.git",
    "MemVR": "https://github.com/1zhou-Wang/MemVR.git",
    "api4sensevoice": "https://github.com/0x5446/api4sensevoice.git",
    "nas-tools": "https://github.com/hsuyelin/nas-tools.git",
    "cdn_cert": "https://github.com/0xJacky/cdn_cert.git",
    "SearchGPT": "https://github.com/Wilson-ZheLin/SearchGPT.git",
    "proXXy": "https://github.com/0xSolanaceae/proXXy.git",
    "Infinite-ISP": "https://github.com/10x-Engineers/Infinite-ISP.git",
    "ROMANCE": "https://github.com/zzq-bot/ROMANCE.git",
    "DreamMat": "https://github.com/zzzyuqing/DreamMat.git",
    "BananaDropFarm": "https://github.com/zZan54/BananaDropFarm.git",
    "python-zulip-api": "https://github.com/zulip/python-zulip-api.git",
    "alas-with-dashboard": "https://github.com/ReDawn2020/Alas-with-Dashboard.git",
    "EmbyToAlist": "https://github.com/zsbai/EmbyToAlist.git",
    "py.wtf": "https://github.com/zsol/py.wtf.git",
    "MuseHeart-MusicBot": "https://github.com/zRitsu/MuseHeart-MusicBot.git",
    "OuteTTS": "https://github.com/edwko/OuteTTS.git",
    "reevo": "https://github.com/ai4co/reevo.git",
    "OmniGen-ComfyUI": "https://github.com/AIFSH/OmniGen-ComfyUI.git",
    "graphrag-practice-chinese": "https://github.com/Airmomo/graphrag-practice-chinese.git",
    "CLAPSep": "https://github.com/Aisaka0v0/CLAPSep.git",
    "logdata-anomaly-miner": "https://github.com/ait-aecid/logdata-anomaly-miner.git",
    "llumnix": "https://github.com/AlibabaPAI/llumnix.git",
    "streamflow": "https://github.com/alpha-unito/streamflow.git",
    "thunor-web": "https://github.com/alubbock/thunor-web.git",
    "ion-python": "https://github.com/amazon-ion/ion-python.git",
    "ai8x-synthesis": "https://github.com/analogdevicesinc/ai8x-synthesis.git",
    "hadith-every-hour": "https://github.com/Ananto30/hadith-every-hour.git",
    "ll-mtproto": "https://github.com/andrew-ld/LL-mtproto.git",
    "ELMo-Tune": "https://github.com/asu-idi/ELMo-Tune.git",
    "Music": "https://github.com/The-HellBot/Music.git",
    "nbss": "https://github.com/SonishMaharjanfuse/nbss.git",
    "Axobot": "https://github.com/Axobot-org/Axobot.git",
    "redroid-script": "https://github.com/ayasa520/redroid-script.git",
    "sydom": "https://github.com/5ymph0en1x/SyDOM.git",
    "trex": "https://github.com/automorphic-ai/trex.git",
    "monster-siren-download": "https://github.com/1n0r1/monster-siren-download.git",
    "adata": "https://github.com/1nchaos/adata.git",
    "FlareSolverr": "https://github.com/FlareSolverr/FlareSolverr.git",
    "cage": "https://github.com/macostea/cage.git",
    "0din": "https://github.com/The0dinProject/0din.git",
    "mABC": "https://github.com/zwpride/mABC.git",
    "SOLANA_SNIPER_BOT": "https://github.com/Xianpwr/SOLANA_SNIPER_BOT.git",
    "toraniko": "https://github.com/0xfdf/toraniko.git",
    "x12306": "https://github.com/0xHJK/x12306.git",
    "SwinUnet3D": "https://github.com/1152545264/SwinUnet3D.git",
    "textual-paint": "https://github.com/1j01/textual-paint.git",
    "funding-rate-arbitrage": "https://github.com/aoki-h-jp/funding-rate-arbitrage.git",
    "stupidocr": "https://github.com/81NewArk/StupidOCR.git",
    "tapes": "https://github.com/a-xavier/tapes.git",
    "ownfoil": "https://github.com/a1ex4/ownfoil.git",
    "a4ksubtitles": "https://github.com/a4k-openproject/a4kSubtitles.git",
    "web-survivalscan": "https://github.com/AabyssZG/Web-SurvivalScan.git",
    "sensAI": "https://github.com/opcode81/sensAI.git",
    "spacy-fi": "https://github.com/aajanki/spacy-fi.git",
    "segad": "https://github.com/abc-125/segad.git",
    "libem": "https://github.com/abcsys/libem.git",
    "pixoo-rest": "https://github.com/4ch1m/pixoo-rest.git",
    "GitHub520": "https://github.com/521xueweihan/GitHub520.git",
    "horus": "https://github.com/6abd/horus.git",
    "meshbot": "https://github.com/868meshbot/meshbot.git",
    "koboldai": "https://github.com/KoboldAI/KoboldAI-Client.git",
    "dfktools": "https://github.com/0rtis/dfktools.git",
    "anubis": "https://github.com/sundaysec/anubis.git",
    "infrastructure": "https://github.com/2i2c-org/infrastructure.git",
    "sa818": "https://github.com/0x9900/SA818.git",
    "Blinks": "https://github.com/0xAnuj/Blinks.git",
    "robofinder": "https://github.com/Spix0r/robofinder.git",
    "o365spray": "https://github.com/0xZDH/o365spray.git",
    "envelope": "https://github.com/1997cui/envelope.git",
    "pyfaas4i": "https://github.com/4intelligence/pyfaas4i.git",
    "freqtrade": "https://github.com/freqtrade/freqtrade.git",
    "keras": "https://github.com/keras-team/keras.git",
    "face_recognition": "https://github.com/ageitgey/face_recognition.git",
    "grok-1": "https://github.com/xai-org/grok-1.git",
    "PaddleOCR": "https://github.com/PaddlePaddle/PaddleOCR.git"
}

CSV_HEADER = ["Repo_Name", "Total Repo Leaks", "Guarddog findings", "Safety findings", "Critical Vulns", "High Vulns", "Medium Vulns", "Low Vulns"]
app = Flask(__name__)

load_dotenv('.env')

SERVICES = json.loads(os.getenv("SERVICES"))
CSV_PATH =  os.getenv("CSV_PATH")
gitleaks_url = SERVICES.get("Gitleaks")
guarddog_url = SERVICES.get("Guarddog")
safety_url = SERVICES.get("Safety")
bearer_url = SERVICES.get("Bearer")
MONGO_SERVICE_URL = os.getenv("MONGO_SERVICE_URL")
API_GATEWAY = os.getenv("API_GATEWAY_URL", "http://api_gateway:5007")


@app.route('/update_db', methods=['POST'])
def update_db():
# Loop over all repositories
    for repo, url in repo_urls.items():
        try:
            # Preparing the payload
            payload = {
                "repo_url": url,
                "tools": ["Gitleaks", "Guarddog", "Safety", "Bearer"]
            }

            # Sending the request to the API Gateway to analyze the repository
            response = requests.post(f"{API_GATEWAY}/analyze", json=payload)
            
            if response.status_code == 200:
                # Get the response data
                response_data = response.json()

                # Bearer Data
                # Bearer Data
                bearer_data = response_data['results']['Bearer']['data']['data']
                critical = bearer_data['critical']
                high = bearer_data['high']
                medium = bearer_data['medium']
                low = bearer_data['low']
                # Check if 'vulnerabilities' is a list or an integer
                bearer_vulnerabilities = len(bearer_data['vulnerabilities']) if isinstance(bearer_data['vulnerabilities'], list) else bearer_data['vulnerabilities']

                # Gitleaks Data
                gitleaks_data = response_data['results']['Gitleaks']['data']['data']
                # Check if 'leaks' is a list or an integer
                gitleaks_leaks = len(gitleaks_data['leaks']) if isinstance(gitleaks_data['leaks'], list) else gitleaks_data['leaks']

                # Guarddog Data
                guarddog_data = response_data['results']['Guarddog']['data']['data']
                # Check if 'results' is a list or a string (no suspicious findings case)
                guarddog_results = 0 if guarddog_data['results'] == 'No suspicious findings' else (len(guarddog_data['results']) if isinstance(guarddog_data['results'], list) else guarddog_data['results'])

                # Safety Data
                safety_data = response_data['results']['Safety']['data']['data']
                # Check if 'vulnerabilities' is a list or an integer
                safety_vulnerabilities = len(safety_data['vulnerabilities']) if isinstance(safety_data['vulnerabilities'], list) else safety_data['vulnerabilities']


                # Print the extracted data for verification
                print(f"Repo Name: {repo}")
                print(f"Bearer: Critical={critical}, High={high}, Medium={medium}, Low={low}, Vulnerabilities={bearer_vulnerabilities}")
                print(f"Gitleaks Leaks: {gitleaks_leaks}")
                print(f"Guarddog Results: {guarddog_results}")
                print(f"Safety Vulnerabilities: {safety_vulnerabilities}")
                
                # Inserting data into the CSV
                with open(CSV_PATH, "a", newline="") as file:
                    writer = csv.writer(file)
                    # Write a new row with the values for the repository
                    writer.writerow([repo, gitleaks_leaks, guarddog_results, safety_vulnerabilities, critical, high, medium, low])

                print("New data has been inserted into the CSV file.")
            else:
                print(f"Error with analysis for {repo}: {response.text}")
        
        except Exception as e:
            print(f"An error occurred for {repo}: {e}")


@app.route('/create_db', methods=['POST'])
def create_db():
    # Open the CSV file in write mode to clear its content and write the header
    with open(CSV_PATH, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)  # Write the header first

    # Loop over all repositories
    for repo, url in repo_urls.items():
        try:
            # Preparing the payload
            payload = {
                "repo_url": url,
                "tools": ["Gitleaks", "Guarddog", "Safety", "Bearer"]
            }

            # Sending the request to the API Gateway to analyze the repository
            response = requests.post(f"{API_GATEWAY}/analyze", json=payload)
            
            if response.status_code == 200:
                # Get the response data
                response_data = response.json()

                # Extract the data for each tool
                bearer_data = response_data['results']['Bearer']['data']['data']
                gitleaks_data = response_data['results']['Gitleaks']['data']['data']
                guarddog_data = response_data['results']['Guarddog']['data']['data']
                safety_data = response_data['results']['Safety']['data']['data']

                # Extract specific values
                critical = bearer_data['critical']
                high = bearer_data['high']
                medium = bearer_data['medium']
                low = bearer_data['low']
                bearer_vulnerabilities = len(bearer_data['vulnerabilities']) if isinstance(bearer_data['vulnerabilities'], list) else bearer_data['vulnerabilities']
                gitleaks_leaks = len(gitleaks_data['leaks']) if isinstance(gitleaks_data['leaks'], list) else gitleaks_data['leaks']
                guarddog_results = 0 if guarddog_data['results'] == 'No suspicious findings' else (len(guarddog_data['results']) if isinstance(guarddog_data['results'], list) else guarddog_data['results'])
                safety_vulnerabilities = len(safety_data['vulnerabilities']) if isinstance(safety_data['vulnerabilities'], list) else safety_data['vulnerabilities']

                # Print the extracted data for verification
                print(f"Repo Name: {repo}")
                print(f"Bearer: Critical={critical}, High={high}, Medium={medium}, Low={low}, Vulnerabilities={bearer_vulnerabilities}")
                print(f"Gitleaks Leaks: {gitleaks_leaks}")
                print(f"Guarddog Results: {guarddog_results}")
                print(f"Safety Vulnerabilities: {safety_vulnerabilities}")

                # Step 2: Append new data to the CSV (after the header)
                with open(CSV_PATH, "a", newline="") as file:  # Open the file in append mode to add new data
                    writer = csv.writer(file)
                    writer.writerow([repo, gitleaks_leaks, guarddog_results, safety_vulnerabilities, critical, high, medium, low])
                print("New data has been inserted into the CSV file.")
            else:
                print(f"Error with analysis for {repo}: {response.text}")
        
        except Exception as e:
            print(f"An error occurred for {repo}: {e}")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5008)
