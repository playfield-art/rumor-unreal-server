import json
from fastapi import FastAPI, HTTPException
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
from graphql_api import get_data, get_languages
from data import sanitize_data, get_data_from_json, get_brainjar_data, format_rumor_data, download_all_audio, update_rumor_data
from pythonosc import udp_client

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
try:
  update_interval = int(os.getenv('DB_UPDATE_INTERVAL'))
except Exception as e:
	update_interval = 15
	print(f"Error: {e}")
UPDATE_GRAPHQL_DATA = (os.getenv('DB_UPDATE_GRAPHQL_DATA', 'False') == 'True')
DOWNLOAD_FOR_BUILD = (os.getenv('DOWNLOAD_FOR_BUILD', 'False') == 'True')
if(DOWNLOAD_FOR_BUILD):
	output_folder = os.getenv('DOWLOAD_FOLDER_QUOTE_FILES_BUILD')
else:
	output_folder = os.getenv('DOWLOAD_FOLDER_QUOTE_FILES')
        

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
    print(f"Next update: {next_update.strftime('%d/%m/%Y %H:%M:%S')}")
    return next_update

def update_database(force_update = False):
    if(force_update):
      print("Forcing update")
    else:
      scheduler.add_job(update_database, 'date', run_date=get_next_update_time())
    # try:
    if True:
        print("Updating database...")
        brainjar_data = get_brainjar_data()
        interation_id = get_data_from_json('id.json')
        # change this to ==

        if (brainjar_data['iteration_id'] == interation_id or brainjar_data['status'] != "done") and not force_update:
            print("No new data available")
            return
        else:
          print("New data available")
          languages = get_languages(headers, db_url)
          if(UPDATE_GRAPHQL_DATA):
            print("Update graphql data")
            graphql_data = get_data(headers, db_url)
            graphql_data_sanitized = sanitize_data(graphql_data)
            all_data = format_rumor_data(brainjar_data, graphql_data_sanitized, languages)
          else:
            print("Don't update graphql data")
            all_data = update_rumor_data(brainjar_data, get_data_from_json('data.json'), languages)
          data_to_use = all_data
          data_to_use['meta_data'] = {
            'last_updated': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'languages': languages,
            'intro_url': 'intro'
            }

          # Save the updated data to 'data.json'
          if data_to_use:
            with open('data.json', 'w') as outfile:
                json.dump(data_to_use, outfile)
            # trigger unreal engine
            if(UPDATE_GRAPHQL_DATA):                                          
              download_all_audio(graphql_data_sanitized, output_folder)
            client.send_message("/update", "")
            print("Update complete")
            try:
              with open('id.json', 'w') as outfile:
                json.dump(brainjar_data['iteration_id'], outfile)
            except Exception as e:
              print(f"Error updating id: {e}")          

      	# trigger unreal engine

    # except Exception as e:
    #     print(f"Error updating database: {e}")
# The job will be executed on the next update time
scheduler.add_job(update_database, 'date', run_date=get_next_update_time())


update_database(True)

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
