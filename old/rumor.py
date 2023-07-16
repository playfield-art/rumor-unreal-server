import requests
from dotenv import load_dotenv
import os
from data import sanitize_data, format_data, getDataFromJson

load_dotenv()
bearer_token_brainjar = os.getenv('BEARER_TOKEN_BRAINJAR')

data_to_use = getDataFromJson('data.json')


def get_rumor_data():
    url = "https://brj-intern-playfield-rumour.ew.r.appspot.com/rumor"
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



def extract_rumor_data(data):
    result = {}
    for section in data['data']['sections']:
        title = section['title']
        tags = [tag['tag'] for tag in section['tags']]
        overall_summary = section['summary']['overall']
        stories = []
        for section_tag in section['tags']:
            print(section_tag['tag'])
            for data_tag in data_to_use:
                print(data_tag)
                if section_tag['tag'].lower() == data_tag.lower():
                    for story in data_to_use[data_tag]:
                      stories.append({'story': story['text'], 'tag': data_tag})
                    
        result[title] = {
            'title': title,
            'tags': tags,
            'summary': overall_summary,
            'stories': stories
        }

            
    return result    

# Example usage
rumor_data = get_rumor_data()


if rumor_data:
    rumor_data = extract_rumor_data(rumor_data)
    print(rumor_data['Arts & culture'])
