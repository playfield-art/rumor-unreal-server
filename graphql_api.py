import os
import requests
import json
from dotenv import load_dotenv

def get_categories(headers, db_url):
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

    response = requests.post(db_url, headers=headers, data=json.dumps({'query': list_categories_query}))

    if response.status_code == 200:
        data = response.json()
        categories = data['data']['questionTags']['data']
        return categories
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")

def get_quotes(headers, db_url, category):
    query = f'''
    query {{
    	quotes(
        filters: {{ active: {{ eq: true }}, question_tag: {{ name: {{ eq: "{category}" }} }} }} 
        pagination: {{ limit: 9999 }}                 
			) {{
    	data {{
      	attributes {{
        	question_tag {{
          data {{
            attributes {{
              name
            }}
          }}
        }}
      }}
      attributes {{
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
      }}
    }}
  }}
  }}
    '''

    response = requests.post(db_url, headers=headers, data=json.dumps({'query': query}))

    if response.status_code == 200:
        data = response.json()
        return data['data']['quotes']['data']
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")

def get_data(headers, db_url):
    data = {}
    categories = get_categories(headers, db_url)
    if categories is not None:
      for category in categories:
        category_name = category['attributes']['name']
        data[category_name] = get_quotes(headers, db_url, category_name)
    return data

def get_languages(headers, db_url):
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


# if __name__ == '__main__':
#     load_dotenv()
#     bearer_token_graphql = os.getenv('BEARER_TOKEN_GRAPHQL')
#     db_url = os.getenv('DB_URL_GRAPHQL')
#     headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     'Authorization': f'Bearer {bearer_token_graphql}'
#      }
#     get_languages(headers, db_url)
    