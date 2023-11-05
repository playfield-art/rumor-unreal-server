import os
import requests

def update_audio_files(new_data, existing_data, output_folder):
    for category, category_data in existing_data.items():
        for section_data in category_data:
            for quote_data in section_data.get('quotes', {}).values():
                for quote in quote_data:
                    audio_id = quote['quote']['en']['audio']['id']
                    
                    if not audio_id:
                        continue  # Skip if the audio ID is missing
                    
                    if any(audio_id in quote['quote'][lang]['audio']['id'] for lang in new_data):
                        # Save and download the audio file
                        url = quote['quote']['en']['audio']['url']
                        download_audio_file(url, output_folder, audio_id)
                    else:
                        # Delete the audio file if it doesn't exist in new data
                        delete_audio_file(output_folder, audio_id)

def download_audio_file(url, output_folder, audio_id):
    response = requests.get(url)
    print(f"Downloading audio file {audio_id}...")
    print(url)
    if response.status_code == 200:
        audio_data = response.content
        file_path = os.path.join(output_folder, f"{audio_id}.wav")
        with open(file_path, 'wb') as audio_file:
            audio_file.write(audio_data)

def delete_audio_file(output_folder, audio_id):
    file_path = os.path.join(output_folder, f"{audio_id}.wav")
    if os.path.exists(file_path):
        os.remove(file_path)