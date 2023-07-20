import json
import random
import requests
from dotenv import load_dotenv
import os
import re

def insert_br_before_long_words(input_string, max_consecutive_chars=20):
    words = re.findall(r'\S+|[.,!?;]', input_string)  # Split words and keep punctuation marks
    result = []
    current_line_length = 0

    for item in words:
        if re.match(r'\S+', item):  # If it's a word
            word_length = len(item)
            if current_line_length + word_length > max_consecutive_chars:
                result.append('<br> ')
                current_line_length = 0

            result.append(item + ' ')
            current_line_length += word_length
        else:  # If it's a punctuation mark
            result.append(item + ' ')
            current_line_length += 1

    return ''.join(result)

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



def format_rumor_data(data, graphql_data, languages):
    result = {}
    short_languages = [language['short'] for language in languages]
    for section in data['data']['sections']:
        title = section['title']
        tags = [tag['tag'] for tag in section['tags']]
        summary = {summary_part: {language: section['summary'][summary_part] for language in short_languages} for summary_part in section['summary']}

        quotes = {tag: [] for tag in tags}
        quotes['overall'] = []
        for section_tag in section['tags']:
            for data_tag in graphql_data:
                if section_tag['tag'].lower() == data_tag.lower():
                    for quote in graphql_data[data_tag]:
                      quote_with_language = {language['short']: '' for language in languages}
                      print(quote_with_language)
                      for translation in quote['translations']:
                        if translation['language']['data']['short'] in short_languages:
                          language = translation['language']['data']['short']
                          text = insert_br_before_long_words(translation['text'], max_consecutive_chars=35)
                          quote_with_language[language] = text
                      quotes[data_tag.lower()].append(quote_with_language)
                      quotes['overall'].append(quote_with_language)
          
        result[title] = {
            'title': {language: title for language in short_languages},
            'summary': summary,
            'quotes': quotes,
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
