import json
import requests
import os
import re
import uuid

def insert_br_before_long_words(input_string: str, max_consecutive_chars:int =20):
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
            sanitized_item = {}
            for k, v in item.items():
                if k == 'translations':  # Special handling for the 'translations' key
                    sanitized_item[k] = {}
                    for translation in v:
                        try:
                            if translation['language']['data'] != None:
                                language = translation['language']['data']['attributes']['short']
                                text = translation['text']
                                sanitized_item[k][language] = text
                        except Exception as e:
                            print(translation)
                            print(f"Error while sanitizing translation: {e}")
                elif k == 'audio':  # Special handling for the 'audio' key
                    sanitized_item[k] = {}
                    for audio in v:
                      language = audio['language']['data']['attributes']['short']
                      sanitized_item[k][language] = {'id': f'{language}_{str(uuid.uuid4())}',  # Generate a unique ID for the audio,
                         'url': audio['audio']['data']['attributes']['url'],
                         } 
                    print(sanitized_item[k])
                else:
                    sanitized_item[k] = sanitize_data(v)
            return sanitized_item
    elif isinstance(item, list):
        return [sanitize_data(i) for i in item]
    else:
        return item



def get_data_from_json(url):
    try:
      with open(url) as json_file:
        data = json.load(json_file)
        return data
    except Exception as e:
        raise Exception(f"Error loading data from '{url}'. Make sure the file exists and contains valid JSON data.") from e 

def get_brainjar_data() -> dict:
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
        raise Exception(f"Error while fetching data from Brainjar API: {e}") from e


def format_rumor_data(data: dict, graphql_data: dict, languages: dict):
    result = {}
    short_languages = [language for language in languages.keys()]
    
    for section in data.get('Buurtleven', []):
        title = section['question_tag']
        tags = []
        summary = {}

        quotes = {tag: [] for tag in tags}
        quotes['overall'] = []

        for section_tag in tags:
            for data_tag in graphql_data.keys():
                if section_tag.lower() == data_tag.lower():
                    for quote in graphql_data[data_tag]:
                        quote_with_language = {language: '' for language in short_languages}
                        for language, text in quote.get('translations', {}).items():
                            if language in short_languages:
                                quote_with_language[language] = insert_br_before_long_words(text, max_consecutive_chars=35)
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
                ]
            }
        }

    return result

def format_rumor_data(data: dict, graphql_data: dict, languages: dict):
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
                      for language in quote['translations']:                         
                        if language in short_languages:
                          text = insert_br_before_long_words(quote['translations'][language], max_consecutive_chars=35)
                          print(quote)
                          if language in quote['audio']:
                            quote_with_language[language] = {'text': text, 'audio': quote['audio'][language]}
                          else:
                            quote_with_language[language] = {'text': text, 'audio': None}
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

def delete_files_in_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted {filename}")
        except Exception as e:
            print(f"Failed to delete {filename}: {str(e)}")

def download_audio(audio_data, output_folder):
    for language, audio_list in audio_data.items():
        for audio_info in audio_list:
            audio_url = audio_info['url']
            audio_id = audio_info['id']
            filename = f"{audio_id}.wav"

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            response = requests.get(audio_url)
            if response.status_code == 200:
                output_path = os.path.join(output_folder, filename)
                with open(output_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {filename}")

def download_all_audio(data, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    delete_files_in_folder(output_folder)
    all_audio_data = {}
    for category_data in data.values():
        for item in category_data:
            if 'audio' in item:
                audio_data = item['audio']
                for language, audio_info in audio_data.items():
                    if language not in all_audio_data:
                        all_audio_data[language] = []
                    all_audio_data[language].append(audio_info)
    download_audio(all_audio_data, output_folder)
