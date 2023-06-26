import json

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
    