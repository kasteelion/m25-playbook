import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL to scrape playbooks
base_url = "https://www.madden-school.com/playbooks/"
target_string = "playbooks"
exclude_strings = ["finder", "search"]

# Data structure to hold the scraped data
data = []

# Step 1: Identify playbooks (team and side)
team_response = requests.get(base_url)
team_soup = BeautifulSoup(team_response.content, 'html.parser')

for a in team_soup.find_all('a', href=True):
    href = a['href']
    if href.startswith('/playbooks/') and target_string in href and not any(exclude_str in href for exclude_str in exclude_strings):
        team_and_side = href.strip('/')
        playbook_url = f"https://www.madden-school.com{href}"
        print(f"Found playbook URL: {playbook_url}")

        # Step 2: Access formations within each playbook
        playbook_response = requests.get(playbook_url)
        playbook_soup = BeautifulSoup(playbook_response.content, 'html.parser')

        for formation_link in playbook_soup.find_all('a', href=True):
            formation_href = formation_link['href']
            if formation_href.startswith(href) and len(formation_href.split('/')) == 4:  # Ensures it goes one level deeper
                formation_url = f"https://www.madden-school.com{formation_href}"
                formation_name = formation_href.split('/')[-2]
                print(f"Found formation URL: {formation_url}")

                # Step 3: Access plays within each formation
                formation_response = requests.get(formation_url)
                formation_soup = BeautifulSoup(formation_response.content, 'html.parser')

                for play_link in formation_soup.find_all('a', href=True):
                    play_href = play_link['href']
                    if play_href.startswith(formation_href) and len(play_href.split('/')) == 5:  # Final level
                        play_url = f"https://www.madden-school.com{play_href}"
                        play_name = play_href.split('/')[-1].replace('-', ' ').title()
                        set_name = play_href.split('/')[-2].replace('-', ' ').title()
                        print(f"Found play URL: {play_url} - Play: {play_name}")

                        # Add data to list
                        data.append({
                            "Offense/Defense": team_and_side.split('/')[-1].title(),
                            "Formation": formation_name.replace('-', ' ').title(),
                            "Set": set_name,
                            "Play": play_name
                        })

# Step 4: Save data to a CSV
df = pd.DataFrame(data)
df.to_csv("madden_playbooks_new2.csv", index=False)
print("Data collection complete and saved to madden_playbooks_new2.csv.")
