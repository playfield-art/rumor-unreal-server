import requests
import os

def get_brainjar_data(language='en') -> dict:
    db_url = os.getenv('DB_URL_BRAINJAR')
    endpoint = '/rumor'
    language_param = f'?lang={language}'
    url = f'{db_url}{endpoint}{language_param}'
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
        raise Exception(
            f"Error while fetching data from Brainjar API: {e}") from e


def get_brainjar_data_all_languages(languages: dict) -> dict:
    data = {}
    print("Fetching data from Brainjar API...")
    for language in languages:
        data[language['short']] = get_brainjar_data(language['short'])
    print("Data fetched")
    return combine_brainjar_languages(data, languages)

def combine_brainjar_languages(original_data, languages):
    print("Combining data from different languages...")
    new_data = {
        'iteration_id': original_data['en']['iteration_id'],
        'datetime': original_data['en']['datetime'],
        'runtime': original_data['en']['runtime'],
        'status': original_data['en']['status'],
        'data': {
            'intro': {lang: original_data[lang]['data']['intro'] for lang in original_data},
            'sections': {},
            'outro': {lang: original_data[lang]['data']['outro'] for lang in original_data}
        }
    }
    
    for section_data in original_data['en']['data']['sections']:
        section_title = section_data['title']
        section_tags = section_data['tags']
        new_data['data']['sections'][section_title] = {
            'title': section_title,
            'tags': section_tags,
            'summary': {tag: {} for tag in section_data['summary']}
        }
    for language in languages:
        for section in original_data[language['short']]['data']['sections']:
            for summary_part in section['summary']:
                title = section['title']
                new_data['data']['sections'][title]['summary'][summary_part][language['short']] = section['summary'][summary_part]
    return new_data


