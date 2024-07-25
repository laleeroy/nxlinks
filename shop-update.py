import json
import requests
import re

# Load your current JSON file
with open('tinfoil.json', 'r') as f:
    data = json.load(f)

# Fetch the README content
url = 'https://raw.githubusercontent.com/carcaschoi/tinfoil-json/main/README.md'
response = requests.get(url)
readme_content = response.text

# Extract the "## Shop Links" section
shop_links_section = re.search(r'## Shop Links\n(.*?)(\n##|\Z)', readme_content, re.DOTALL).group(1)

# Extract shop links and titles from the "## Shop Links" section
shop_links = re.findall(r'Protocol: https\nHost: (.*?)\nTitle: (.*?)\n', shop_links_section)
new_locations = [{"url": f"https://{link[0]}", "title": link[1], "action": "add"} for link in shop_links]

# Update the locations in the JSON file
existing_urls = [location["url"] for location in data["locations"]]
data['locations'] = [location for location in data['locations'] if location["url"] in existing_urls] + \
                    [location for location in new_locations if location["url"] not in existing_urls]

# Write updated JSON to file
with open('tinfoil.json', 'w') as f:
    json.dump(data, f, indent=4)

print("tinfoil.json has been updated successfully.")
