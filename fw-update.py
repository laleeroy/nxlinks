import requests
import json
import os
import re

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

def get_firmware_releases(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    releases = response.json()
    
    firmware_releases = {}
    for release in releases:
        title = release['name']
        # Check if the release title does not contain "(Rebootless Update)"
        if not re.search(r'\(Rebootless Update\b', title):
            for asset in release['assets']:
                if asset['name'].endswith('.zip'):  # Ensure we get the correct asset
                    download_url = asset['browser_download_url']
                    firmware_releases[title] = download_url
                    break  # Assuming there is only one relevant asset per release

    return firmware_releases

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

def update_firmware_releases(updates, firmware_releases):
    if 'firmwares' not in updates:
        updates['firmwares'] = {}

    current_firmwares = updates['firmwares']
    new_entries = {title: url for title, url in firmware_releases.items() if title not in current_firmwares}
    
    if new_entries:
        updates['firmwares'].update(new_entries)
        return True

    return False

def main():
    api_url_cfw = 'https://api.github.com/repos/laleeroy/nxcfw/releases/latest'
    api_url_firmware = 'https://api.github.com/repos/THZoria/NX_Firmware/releases'
    updates_file_path = 'updates.json'

    try:
        latest_release = get_latest_release(api_url_cfw)
        tag_name, title, download_url = extract_release_data(latest_release)

        if not download_url:
            print("No suitable download URL found in the latest cfw release.")
        else:
            updates = load_updates(updates_file_path)
            if update_json_with_latest_release(updates, tag_name, title, download_url):
                save_updates(updates_file_path, updates)
                print("updates.json has been updated with the latest cfw release.")
            else:
                print("The latest cfw release is already up-to-date in updates.json.")

        firmware_releases = get_firmware_releases(api_url_firmware)
        if update_firmware_releases(updates, firmware_releases):
            save_updates(updates_file_path, updates)
            print("updates.json has been updated with the latest firmware releases.")
        else:
            print("Firmware releases are already up-to-date in updates.json.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
