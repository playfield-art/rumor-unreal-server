import json
import random
import requests
from dotenv import load_dotenv
import os


def sanitize_data(item):
    if isinstance(item, dict):
        if "attributes" in item:
            return sanitize_data(item["attributes"])
        else:
            return {k: sanitize_data(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [sanitize_data(i) for i in item]
    else:
        return item

def format_data(data):
    # add local url
    return data

def getDataFromJson(url):
    with open(url) as json_file:
        data = json.load(json_file)
        return data

def get_brainjar_data():
    url = "https://brj-intern-playfield-rumour.ew.r.appspot.com/rumor"
    bearer_token_brainjar = os.getenv('BEARER_TOKEN_BRAINJAR')
    headers = {
        "Authorization": f"Bearer {bearer_token_brainjar}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None



def format_rumor_data(data, graphql_data):
    result = {}
    
    for section in data['data']['sections']:
        title = section['title']
        tags = [tag['tag'] for tag in section['tags']]
        summary = section['summary']
        stories = {tag: [] for tag in tags}
        for story in stories:
            print(story)
        for section_tag in section['tags']:
            for data_tag in graphql_data:
                if section_tag['tag'].lower() == data_tag.lower():
                    for story in graphql_data[data_tag]:
                      stories[data_tag.lower()].append(story['text'])
                    
        result[title] = {
            'title': title,
            'summary': summary,
            'stories': stories,
            'meta': {
                'introUrl': 'sfsdf.url',
                'tags': tags,
                'statistics': [
                    { 
                        'name': "amount_of_family_members", 
                     'label': "Amount of family member", 
										 'type': "percentage", 
                    'value': "30" 
										},
								]}
						},
        

            
    return result    
