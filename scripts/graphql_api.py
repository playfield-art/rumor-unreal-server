import os
import requests
import json

def get_categories(headers: dict, db_url: str):
    list_categories_query = '''
    {
      questionTags(pagination: { limit: 100 }) {
        data {
          attributes {
            name
          }
        }
      }
    }
    '''
    try:
      response = requests.post(db_url, headers=headers, data=json.dumps({'query': list_categories_query}))

      if response.status_code == 200:
        data = response.json()
        categories = data['data']['questionTags']['data']
        return categories
      else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error while fetching categories: {e}") from e

def get_quotes(headers, db_url, category):
    query = f'''
    query {{
    	quotes(
        filters: {{ active: {{ eq: true }}, question_tag: {{ name: {{ eq: "{category}" }} }} }} 
        pagination: {{ limit: 9999 }}                 
			) {{
    	data {{
        id
      	attributes {{
        	question_tag {{
          data {{
            attributes {{
              name
            }}
          }}

        }}
        highlighted
        translations {{
          language {{
            data {{
              attributes {{
                short
                long
              }}
            }}
          }}
          text
        }}
        audio {{
          audio {{
            data {{
              id
              attributes {{
                url
              }}
            }}
          }}
          language {{
            data {{
              attributes {{
                short
              }}
            }}
          }}
        }}
      }}
    }}
  }}
  }}
    '''

    try:
        response = requests.post(db_url, headers=headers, data=json.dumps({'query': query}))

        if response.status_code == 200:
            data = response.json()
            return data['data']['quotes']['data']
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error while fetching quotes for category '{category}': {e}") from e

def get_data(headers: dict, db_url: str) -> dict:
    data = {}
    categories = get_categories(headers, db_url)
    if categories is not None:
      for category in categories:
        category_name = category['attributes']['name']
        data[category_name] = get_quotes(headers, db_url, category_name)
    return data

def get_languages(headers: dict, db_url: str):
    query = '''
				{
			languages {
				data {
					attributes {
						short
						long
					}
				}
			}
		}
			'''
    try:
        response = requests.post(db_url, headers=headers, data=json.dumps({'query': query}))
        if response.status_code == 200:
            data = response.json()
            mapped_data = []
            for item in data['data']['languages']['data']:
                attributes = item['attributes']
                mapped_data.append(attributes)
            return mapped_data
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error while fetching languages: {e}") from e

    