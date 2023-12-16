

import requests
import pandas as pd

# List of animal names
animal_names = ['wren', 'eagle', 'duck', 'goose', 'hawk']

# Your API key
api_key = 'CXB3b8nRZ4aBWVCDRxQrIA==EYhqF5PbRwdosJOz'  # Replace with your actual API key

# Initialize an empty list to store the data
data = []

# Loop through each animal name
for name in animal_names:
    api_url = f'https://api.api-ninjas.com/v1/animals?name={name}'
    response = requests.get(api_url, headers={'X-Api-Key': api_key})
    if response.status_code == requests.codes.ok:
        response_data = response.json()
        if response_data:
            for entry in response_data:
                # Check if 'characteristics' key is present
                if 'characteristics' in entry:
                    # Extract 'color' field from 'characteristics'
                    color = entry['characteristics'].get('color', 'Not specified')
                    entry['color'] = color  # Add 'color' field to the entry
                else:
                    entry['color'] = 'Not specified'  # Default value if 'characteristics' not present
                
                # Now append the modified entry to our data list
                data.append(entry)
        else:
            print(f"No data returned for {name}")
    else:
        print("Error:", response.status_code, response.text)

# Create a DataFrame from the modified data
df = pd.DataFrame(data)

# Select the columns we're interested in (if you want to reduce the data further)
df = df[['name', 'color']]  # Add other fields as needed

# Write the DataFrame to a CSV file
csv_file_name = 'apibird.csv'
df.to_csv(csv_file_name, index=False)

print(f"Data written to {csv_file_name}")
