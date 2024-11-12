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

# Check if the request was successful
if team_response.status_code != 200:
    print("Failed to retrieve the main playbooks page.")
else:
    soup = BeautifulSoup(team_response.content, 'html.parser')

    # Find and filter playbook links
    for a in soup.find_all('a'):
        href = a.get('href')
        
        # Filtering for playbooks
        if href and href.startswith('/playbooks/') and target_string in href:
            if any(exclude_str in href for exclude_str in exclude_strings):
                continue  # Skip if the link contains excluded strings

            team_and_side = '/'.join(href.split('/')[2:])
            team_url = f"{base_url}/playbooks/{team_and_side}"

            # Fetch the team playbook page
            team_response = requests.get(team_url)
            if team_response.status_code != 200:
                print(f"Failed to retrieve page for: {team_url}")
                continue

            team_soup = BeautifulSoup(team_response.content, 'html.parser')

            # Extract formations or additional details
            for b in team_soup.find_all('a'):
                formation_href = b.get('href')
                if formation_href and formation_href.startswith(f"/playbooks/{team_and_side}") and "plays" not in formation_href:
                    formation_url = f"{base_url}{formation_href}"
                    formation_name = formation_href.split('/')[-1]  # e.g., "shotgun", "singleback"

                    # Fetch the formation page
                    formation_response = requests.get(formation_url)
                    if formation_response.status_code != 200:
                        print(f"Failed to retrieve formation page for: {formation_url}")
                        continue

                    formation_soup = BeautifulSoup(formation_response.content, 'html.parser')

                    # Extract sets within the formation
                    for set_link in formation_soup.find_all('a'):
                        set_href = set_link.get('href')
                        if set_href and set_href.startswith(formation_href) and "plays" in set_href:
                            set_url = f"{base_url}{set_href}"
                            set_name = set_href.split('/')[-1]  # e.g., "Tight Flex", "Wing Pair"

                            # Fetch the set page
                            set_response = requests.get(set_url)
                            if set_response.status_code != 200:
                                print(f"Failed to retrieve set page for: {set_url}")
                                continue

                            set_soup = BeautifulSoup(set_response.content, 'html.parser')

                            # Extract plays within the set
                            for play_link in set_soup.find_all('a'):
                                play_href = play_link.get('href')
                                if play_href and play_href.startswith(set_href):
                                    play_name = play_href.split('/')[-1]  # e.g., "PA Post Shot", "Four Verticals"

                                    # Append data to the list as a dictionary
                                    data.append({
                                        "Playbook": team_and_side,    # e.g., team and side (offense or defense)
                                        "Formation": formation_name,  # e.g., "shotgun", "singleback"
                                        "Set": set_name,              # e.g., "Tight Flex", "Wing Pair"
                                        "Play": play_name             # e.g., "PA Post Shot", "Four Verticals"
                                    })
                                    print(f"Added play: {play_name} under set {set_name}, formation {formation_name}, playbook {team_and_side}")

# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(data)

# Check if data was collected
if df.empty:
    print("No data was collected.")
else:
    # Save DataFrame to CSV
    df.to_csv("madden_playbooks_detailed.csv", index=False)
    print("Data saved to madden_playbooks_detailed.csv")
