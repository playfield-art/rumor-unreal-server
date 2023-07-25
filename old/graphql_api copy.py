import requests
import json

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
            text
            question_tag {{
              data {{
                attributes {{
                  name
                }}
              }}
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
    for category in categories:
        category_name = category['attributes']['name']
        data[category_name] = get_quotes(headers, db_url, category_name)
    return data
