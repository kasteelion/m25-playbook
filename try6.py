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

# Step 1: Send a GET request to the main playbooks page
url1 = f"{base_url}/playbooks/"
main_response = requests.get(url1)
main_soup = BeautifulSoup(main_response.content, 'html.parser')

# Step 2: Find and filter playbook links (teams and sides)
for a in main_soup.find_all('a', href=True):
    href = a['href']

    # Step 2a: Filter for valid playbooks only
    if href.startswith('/playbooks/') and target_string in href:
        if any(exclude_str in href for exclude_str in exclude_strings):
            continue  # Skip excluded URLs

        # Construct URL for the team and side (offense/defense)
        team_and_side = href.strip('/')
        team_url = f"{base_url}{href}"
        print(f"Accessing team playbook URL: {team_url}")

        # Step 3: Fetch the team playbook page (for formations)
        team_response = requests.get(team_url)
        team_soup = BeautifulSoup(team_response.content, 'html.parser')

        # Step 4: Identify formations within the team playbook
        for b in team_soup.find_all('a', href=True):
            formation_href = b['href']
            if formation_href.startswith(f"/{team_and_side}") and len(formation_href.split('/')) == 4:
                formation_url = f"{base_url}{formation_href}"
                formation_name = formation_href.split('/')[-1].replace('-', ' ').title()
                print(f"Found formation URL: {formation_url}")

                # Step 5: Fetch the formation page to find plays
                formation_response = requests.get(formation_url)
                formation_soup = BeautifulSoup(formation_response.content, 'html.parser')

                # Step 6: Identify plays within each formation
                for play_link in formation_soup.find_all('a', href=True):
                    play_href = play_link['href']
                    if play_href.startswith(formation_href) and len(play_href.split('/')) == 5:
                        play_url = f"{base_url}{play_href}"
                        play_name = play_href.split('/')[-1].replace('-', ' ').title()
                        set_name = play_href.split('/')[-2].replace('-', ' ').title()
                        print(f"Found play URL: {play_url} - Play: {play_name}")

                        # Append data to the list
                        data.append({
                            "Team Playbook": team_and_side.split('/')[-1].title(),
                            "Formation": formation_name,
                            "Set": set_name,
                            "Play": play_name,
                            "Play URL": play_url
                        })

# Step 7: Convert collected data to DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv("madden_playbooks_detailed.csv", index=False)
print("Data saved to madden_playbooks_detailed.csv")
