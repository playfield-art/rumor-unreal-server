import json
from fastapi import FastAPI
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
from graphql_api import get_data, get_languages
from data import sanitize_data, format_data, getDataFromJson, get_brainjar_data, format_rumor_data

load_dotenv()
bearer_token_graphql = os.getenv('BEARER_TOKEN_GRAPHQL')
db_url = os.getenv('DB_URL_GRAPHQL')
update_interval = 5
# session_id = null te schrijven naar bestand
data_to_use = ''

data_to_use = getDataFromJson('data.json')

app = FastAPI()

# Start the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {bearer_token_graphql}'
}

def get_next_update_time():
    today = datetime.now()
    next_update = today + timedelta(minutes=update_interval)
    return next_update

# Define the function that is to be executed
def update_database():
    print("Updating database...")
    languages = get_languages(headers, db_url)
    graphql_data = get_data(headers, db_url)
    graphql_data_sanitized = sanitize_data(graphql_data)
    graphql_formatted_data = format_data(graphql_data_sanitized)
    brainjar_data = get_brainjar_data()
    all_data = format_rumor_data(brainjar_data, graphql_formatted_data, languages)
    global data_to_use
    data_to_use = all_data
    data_to_use['meta_data'] = {
        'last_updated': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'languages': languages,
        'intro_url': 'intro'
		}

    print(data_to_use)
    if graphql_data:
        with open('data.json', 'w') as outfile:
          json.dump(data_to_use, outfile)
    # trigger unreal engine
    scheduler.add_job(update_database, 'date', run_date=get_next_update_time())

# The job will be executed on the next update time
scheduler.add_job(update_database, 'date', run_date=get_next_update_time())

update_database()

@app.get("/api/data")
async def get_data_api():
    return data_to_use

@app.get("/api/categories")
async def get_categories_api():
    return {"categories": list(data_to_use.keys())}