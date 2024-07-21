import requests
import json
import os

def get_latest_release(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()

def extract_release_data(release):
    tag_name = release['tag_name']
    title = release['name']
    download_url = None

    print("Assets found in the latest release:")
    for asset in release['assets']:
        print(f" - {asset['name']}")
        if '8bp' in asset['name'].lower():
            download_url = asset['browser_download_url']
            break

    return tag_name, title, download_url

def load_updates(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def save_updates(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def update_json_with_latest_release(updates, tag_name, title, download_url):
    if 'cfws' not in updates:
        updates['cfws'] = {}
    if 'Atmosphere' not in updates['cfws']:
        updates['cfws']['Atmosphere'] = {}

    current_entries = updates['cfws']['Atmosphere']
    latest_entry_exists = any(
        '[Latest]' in key and download_url == current_entries[key] for key in current_entries
    )

    if not latest_entry_exists:
        updated_entries = {key.replace('[Latest]', '').strip(): value for key, value in current_entries.items()}
        
        # Remove extra spaces in keys
        updated_entries = {key.replace('  ', ' ').strip(): value for key, value in updated_entries.items()}
        
        new_entry_name = f'8BP {tag_name} [Latest] - {title}'
        updated_entries = {new_entry_name: download_url, **updated_entries}
        updates['cfws']['Atmosphere'] = updated_entries

        return True

    return False

def main():
    api_url = 'https://api.github.com/repos/laleeroy/nxcfw/releases/latest'
    updates_file_path = 'updates.json'

    try:
        latest_release = get_latest_release(api_url)
        tag_name, title, download_url = extract_release_data(latest_release)

        if not download_url:
            print("No suitable download URL found in the latest release.")
            return

        updates = load_updates(updates_file_path)

        if update_json_with_latest_release(updates, tag_name, title, download_url):
            save_updates(updates_file_path, updates)
            print("updates.json has been updated with the latest release.")
        else:
            print("The latest release is already up-to-date in updates.json.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
