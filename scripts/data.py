import json
import sys
import requests
import os
from scripts.utils import change_quotation_marks, break_after_title, insert_br_before_long_words, translate_function
import uuid
try:
    import translators as ts
except Exception:
    print("Could not import translators. Make sure you have installed the required dependencies by running 'pip install -r requirements.txt'.")


# def sanitize_data(item):
#     if isinstance(item, dict):
#         if "attributes" in item:
#             return sanitize_data(item["attributes"])
#         else:
#             sanitized_item = {}
#             try:
#                 for k, v in item.items():
#                     if k == 'translations':  # Special handling for the 'translations' key
#                         sanitized_item[k] = {}
#                         for translation in v:
#                             try:
#                                 if translation['language']['data'] != None:
#                                     language = translation['language']['data']['attributes']['short']
#                                     text = translation['text']
#                                     sanitized_item[k][language] = text
#                             except Exception as e:
#                                 print(
#                                     f"Error while sanitizing translation: {e}")
#                     elif k == 'audio':  # Special handling for the 'audio' key
#                         sanitized_item[k] = {}
#                         for audio in v:
#                             try:
#                                 if audio['language']['data'] != None:
#                                     language = audio['language']['data']['attributes']['short']
#                                     sanitized_item[k][language] = {'id': f'{language}_{str(uuid.uuid4())}',  # Generate a unique ID for the audio,
#                                                                    'url': audio['audio']['data']['attributes']['url'],
#                                                                    }
#                             except Exception as e:
#                                 print(
#                                     f"Error while sanitizing translation: {e}")
#                     else:
#                         sanitized_item[k] = sanitize_data(v)
#             except Exception as e:
#                 print(f"Error while sanitizing dict: {e}")
#             return sanitized_item
#     elif isinstance(item, list):
#         return [sanitize_data(i) for i in item]
#     else:
#         return item

def sanitize_data(item):
    if isinstance(item, dict):
        sanitized_item = {}
        for k, v in item.items():
            if k == 'translations' and isinstance(v, list):
                sanitized_item[k] = {translation['language']['data']['attributes']['short']: translation['text']
                                     for translation in v if translation.get('language', {}).get('data')}
            elif k == 'audio' and isinstance(v, list):
                print(k)
                sanitized_item[k] = {audio['language']['data']['attributes']['short']: {
                    'id': f"{audio['language']['data']['attributes']['short']}",
                    'url': audio['audio']['data']['attributes']['url'],
                } for audio in v if audio.get('language', {}).get('data')}
            else:
                sanitized_item[k] = sanitize_data(v)
        return sanitized_item
    elif isinstance(item, list):
        return [sanitize_data(i) for i in item]
    else:
        return item


def format_rumor_data(data: dict, graphql_data: dict, languages: dict):
    result = {}
    short_languages = [language['short'] for language in languages]
    for section_name, section_data in data['data']['sections'].items():
        title = section_data['title']
        tags = [tag['tag'] for tag in section_data['tags']]
        # Initialize an empty dictionary to store the translated summaries
        summary = {}

        # Iterate through each summary part in the section's summary
        for summary_part in section_data['summary']:
            # Initialize a dictionary for the current summary part
            summary[summary_part] = {}

            # Iterate through each language in the list of short_languages
            for language in short_languages:
                summary[summary_part][language] = section_data['summary'][language][summary_part]
        # summary = {summary_part: {language: section['summary'][summary_part] for language in short_languages} for summary_part in section['summary']}

        quotes = {tag: [] for tag in tags}
        quotes['overall'] = []
        for section_tag in section_data['tags']:
            for data_tag in graphql_data:
                if section_tag['tag'].lower() == data_tag.lower():
                    for quote in graphql_data[data_tag]:
                        quote_with_language = {
                            language['short']: '' for language in languages}
                        for language in quote['translations']:
                            if language in short_languages:
                                text = quote['translations'][language]
                                text = change_quotation_marks(text)
                                text = break_after_title(text)
                                quoteTitle = text.split('<stopTitle>')[0]
                                quoteText = insert_br_before_long_words(
                                    text.split('<stopTitle>')[1], max_consecutive_chars=35)
                                text = quoteTitle + quoteText
                                if language in quote['audio']:
                                    quote_with_language[language] = {
                                        'text': text, 'audio': quote['audio'][language]}
                                else:
                                    quote_with_language[language] = {
                                        'text': text, 'audio': None}
                        quote_with_metadata = {
                            'highlighted': quote['highlighted'], 'quote': quote_with_language}
                        quotes[data_tag.lower()].append(quote_with_metadata)
                        quotes['overall'].append(quote_with_metadata)
        translated_titles = {}
        for language in short_languages:
            if language == 'en':
                translated_titles[language] = title
            else:
                translation = translate_function(
                    title, language, 'en', 'alibaba')
                translated_titles[language] = translation
        result[title] = {
            'title': translated_titles,
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


def update_rumor_data(data: dict, old_data: dict, languages: dict):
    print("Updating rumor data...")
    try:
        short_languages = [language['short'] for language in languages]
        
        for section_name, section_data in data['data']['sections'].items():
            title = section_data['title']
            # Initialize an empty dictionary to store the translated summaries
            summary = {}
            
            # Iterate through each summary part in the section's summary
            for summary_part, languages_data in section_data['summary'].items():
                summary[summary_part] = {}
                
                # Iterate through each language in the list of short_languages
                for language in short_languages:
                    if language in languages_data:
                        summary[summary_part][language] = languages_data[language]
                        
            if title in old_data:
                old_data[title][0]['summary'] = summary
    except Exception as e:
        print(f"Error while updating rumor data: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    return old_data
