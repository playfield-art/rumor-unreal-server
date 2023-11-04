import json
import os
import re
import requests
import sys

def break_after_title(text):
    replacements = {
        "donated": "donated<br>",
        "geschonken": "geschonken<br>",
        ":": "",
        "2023": "2023<br><stopTitle>",
        "2022": "2022<br><stopTitle>",
        "2024": "2024<br><stopTitle>"
    }

    for key, value in replacements.items():
        text = text.replace(key, value)

    return text

def change_quotation_marks(text):
    text.replace('”', '"')
    text.replace('“', '"')
    return text

def insert_br_before_long_words(input_string: str, max_consecutive_chars: int = 20):
    # Split words and keep punctuation marks
    words = re.findall(r'\S+|[.,!?;]', input_string)
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


def download_audio(audio_data, output_folder):
    print("Downloading audio...")
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
    print("Downloading audio...")
    print(data)
    for category_data in data.values():
        for item in category_data:
            if 'audio' in item:
                audio_data = item['audio']
                for language, audio_info in audio_data.items():
                    if language not in all_audio_data:
                        all_audio_data[language] = []
                    all_audio_data[language].append(audio_info)
    print(all_audio_data)
    download_audio(all_audio_data, output_folder)

# Function to perform translation from source language (nl) to target language
def translate_function(text, target_lang, src_lang='auto', engine='google'):
    # print(f"Translating '{text}' to {target_lang} using {engine}")
    # print(f"Source language: {src_lang}")
    if engine == 'myMemory' and target_lang == 'en':
        target_lang = 'en-GB'
    try:
        if 'ts' not in sys.modules:
            import translators as ts
        translated_text = ts.translate_text(
            text, engine, src_lang, target_lang)
    except Exception as e:
        raise Exception(f"Error while translating text: {e}") from e
    return translated_text

def delete_files_in_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted {filename}")
        except Exception as e:
            print(f"Failed to delete {filename}: {str(e)}")
            


def get_data_from_json(url):
    try:
        with open(url) as json_file:
            data = json.load(json_file)
            return data
    except Exception as e:
        raise Exception(
            f"Error loading data from '{url}'. Make sure the file exists and contains valid JSON data.") from e

def check_quotes(graphql_data, json_data):
    print("Checking quotes...")
    for section in json_data:
        pass
        # print(json_data[section])
        # for subsection in json_data[section]['summary']:
        #     for quote in json_data[section]['summary'][subsection]:
        #         print(quote)
    for section in graphql_data:
        # print(section)
        pass
        for quote in graphql_data[section]:
            pass
            # if quote['id'] not in json_data['quotes']:
            #     pass

    #             if summary_part in json_data['data']['sections'][section['title']]['summary']:
    #                 if language['short'] not in json_data['data']['sections'][section['title']]['summary'][summary_part]:
    #                     json_data['data']['sections'][section['title']]['summary'][summary_part][language['short']] = []
    #                 for quote in section['summary'][summary_part][language['short']]:
    #                     if quote['text'] not in json_data['data']['sections'][section['title']]['summary'][summary_part][language['short']]:
    #                         json_data['data']['sections'][section['title']]['summary'][summary_part][language['short']].append(quote['text'])
    # print(json_data)
    return graphql_data