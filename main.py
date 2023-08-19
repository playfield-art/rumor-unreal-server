import json
from fastapi import FastAPI, HTTPException
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
from graphql_api import get_data, get_languages
from data import sanitize_data, get_data_from_json, get_brainjar_data, format_rumor_data, download_all_audio

from pythonosc import udp_client

output_folder = "../rumor-unreal/dynamic_audio_files"

# Load environment variables from .env file
try:
    load_dotenv()
except Exception as e:
    raise Exception("Error loading environment variables. Make sure you have a valid .env file.") from e

# Setup OSC client
if os.getenv('OSC_IP') and os.getenv('OSC_PORT'):
	client = udp_client.SimpleUDPClient(os.getenv('OSC_IP'), int(os.getenv('OSC_PORT')))


# Fetch environment variables
bearer_token_graphql = os.getenv('BEARER_TOKEN_GRAPHQL')
db_url = os.getenv('DB_URL_GRAPHQL')
update_interval = 5

# Load initial data from 'data.json' with error handling
try:
    data_to_use = get_data_from_json('data.json')
except Exception as e:
    print(f"Error: {e}")
    # data_to_use = {}

app = FastAPI()

# Start the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {bearer_token_graphql}'
}

def get_next_update_time() -> datetime:
    today = datetime.now()
    next_update = today + timedelta(minutes=update_interval)
    return next_update

def update_database():
    # try:
        print("Updating database...")

        
        
        brainjar_data = get_brainjar_data()
        interation_id = get_data_from_json('id.json')
        # change this to ==
        if brainjar_data['iteration_id'] == interation_id:
            print("No new data available")
            return
        else:
          print("New data available")
          try:
            with open('id.json', 'w') as outfile:
               json.dump(brainjar_data['iteration_id'], outfile)
          except Exception as e:
            print(f"Error updating id: {e}")
          languages = get_languages(headers, db_url)
          graphql_data = get_data(headers, db_url)
          graphql_data_sanitized = sanitize_data(graphql_data)
          download_all_audio(graphql_data_sanitized, output_folder)
          all_data = format_rumor_data(brainjar_data, graphql_data_sanitized, languages)
          print(all_data)
          data_to_use = all_data
          data_to_use['meta_data'] = {
            'last_updated': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'languages': languages,
            'intro_url': 'intro'
        }

          # Save the updated data to 'data.json'
          if graphql_data:
            with open('data.json', 'w') as outfile:
                json.dump(data_to_use, outfile)
            # trigger unreal engine
            client.send_message("/update", "")
          

      	# trigger unreal engine
        scheduler.add_job(update_database, 'date', run_date=get_next_update_time())

    # except Exception as e:
    #     print(f"Error updating database: {e}")

# The job will be executed on the next update time
scheduler.add_job(update_database, 'date', run_date=get_next_update_time())

update_database()

@app.get("/api/data")
async def get_data_api() -> dict:
    if get_data_from_json('data.json'):
        return get_data_from_json('data.json')
    else:
        raise HTTPException(status_code=500, detail="Data is not available.")

@app.get("/api/categories")
async def get_categories_api() -> dict:
    if data_to_use:
        return {"categories": list(data_to_use.keys())}
    else:
        raise HTTPException(status_code=500, detail="Data is not available.")
