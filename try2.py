import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define base URL
base_url = "https://www.madden-school.com"

# Target and exclusion strings
target_string = "playbooks"
exclude_strings = ["finder", "search"]

# List to store data
data = []

# Send a GET request to the main playbooks page
url1 = f"{base_url}/playbooks/"
team_response = requests.get(url1)
soup = BeautifulSoup(team_response.content, 'html.parser')

# Find and filter playbook links
for a in soup.find_all('a'):
    # Getting all hrefs
    href = a.get('href')

    # Filtering for playbooks
    if href and href.startswith('/playbooks/') and target_string in href:
        # Exclude anything that isn't a playbook
        if any(exclude_str in href for exclude_str in exclude_strings):
            continue  # Skip this iteration if an exclude string is found
        
        # Construct team-specific URL
        team_and_side = '/'.join(href.split('/')[2:])  # Gets team and side (e.g., offense or defense)
        team_url = f"{base_url}/playbooks/{team_and_side}"

        # Fetch the team playbook page
        team_response = requests.get(team_url)
        team_soup = BeautifulSoup(team_response.content, 'html.parser')

        # Extract formations or additional details
        for b in team_soup.find_all('a'):
            formation_href = b.get('href')
            if formation_href and formation_href.startswith(f"/playbooks/{team_and_side}") and "plays" not in formation_href:
                formation_url = f"{base_url}{formation_href}"
                formation_name = formation_href.split('/')[-1]

                # Fetch the formation page
                formation_response = requests.get(formation_url)
                formation_soup = BeautifulSoup(formation_response.content, 'html.parser')

                # Extract plays within the formation
                for play_link in formation_soup.find_all('a'):
                    play_href = play_link.get('href')
                    if play_href and play_href.startswith(formation_href) and "plays" in play_href:
                        play_url = f"{base_url}{play_href}"
                        play_name = play_href.split('/')[-1]

                        # Append data to the list as a dictionary
                        data.append({
                            "Team Playbook URL": team_url,
                            "Formation URL": formation_url,
                            "Formation Name": formation_name,
                            "Play URL": play_url,
                            "Play Name": play_name
                        })

# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(data)

# Save DataFrame to CSV
df.to_csv("madden_playbooks_detailed.csv", index=False)
print("Data saved to madden_playbooks_detailed.csv")
