from fastapi import FastAPI
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
from api import get_data, get_categories
from data import sanitize_data, format_data, getDataFromJson

load_dotenv()
bearer_token = os.getenv('BEARER_TOKEN')
db_url = os.getenv('DB_URL')
update_interval = 1
data_to_use = ''

data_to_use = getDataFromJson('data.json')

app = FastAPI()

# Start the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {bearer_token}'
}

def get_next_update_time():
    today = datetime.now()
    next_update = today + timedelta(days=update_interval)
    return next_update

# Define the function that is to be executed
def update_database():
    data = get_data(headers, db_url)
    formatted_data = sanitize_data(data)
    global data_to_use
    data_to_use = format_data(formatted_data)
    scheduler.add_job(update_database, 'date', run_date=get_next_update_time())

# The job will be executed on the next update time
scheduler.add_job(update_database, 'date', run_date=get_next_update_time())

@app.get("/api/data")
async def get_data():
    return data_to_use
    return {
   "purchaseToken":"some-token-value",
   "orderId":"abc123",
   "purchaseTime":"6",
   "isValid": 'false',
}

@app.get("/api/categories")
async def get_categories():
    return {"categories": list(data_to_use.keys())}