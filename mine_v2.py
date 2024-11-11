import requests
from bs4 import BeautifulSoup
# import argparse
# import pandas as pd

# Base URL for playbook pages
BASE_URL = "https://www.madden-school.com/playbooks"


# TODO: Add argparse functionality.
# TODO: Export data to pandas for formatting.

# Step 1: Function to get the team and side URLs
def get_team_data(pageData):
    

    # Parse the initial page
    soup = BeautifulSoup(pageData.content, 'html.parser')
    #print(soup)

    # Find the playbooks section
    # playbook_sections = soup.find('div', class_='flex justify-center gap-x-1 flex-row flex-wrap mb-6')

    # Look for a container that likely holds the team playbooks
    playbook_sections = soup.find_all('div', class_='flex justify-center gap-x-1 flex-row flex-wrap mb-6')
    
    if not playbook_sections:
        print(f"No playbook sections found.")
        return None
    
    #print(f"Playbooks section raw: {playbook_sections}")

    
    teams = {}
    playbooks = {}


    for idx, section in enumerate(playbook_sections, start=1):
        # You can give each section a name based on its position or based on specific text/attributes in the section
        section_name = f"Playbook {idx}"
        
        # Store the section in the dictionary, with each section as a key
        playbooks[section_name] = get_formations_and_plays(section)

    if playbook_sections:
        # Print the section to check what it contains
        #print(f"Playbooks Section: {playbook_sections}")

        # Look for all <a> tags inside the playbook_sections
        a_tags = playbook_sections.find_all('a', href=True)
        # print(f"Found {len(a_tags)} <a> tags: {a_tags}")

        # Loop through each <a> tag to get team names and URLs
        for a_tag in a_tags:
            # Get the team name from the <span> tag inside <a>
            team_name = a_tag.find('span').text.strip()
            side = a_tag['href'].split('/')[-2]  # Extract the side (e.g., 'offense')

            # Get the relative URL from the 'href' and make sure there's no duplicate '/playbooks'
            relative_url = a_tag['href'].lstrip('/')  # Strip leading slashes
            if relative_url.startswith("playbooks/"):
                relative_url = relative_url[len("playbooks/"):]

            team_url = BASE_URL + '/' + relative_url

            teams[team_name] = {'side': side, 'url': team_url}

        # print(f"Teams: {teams}")

    else:
        print("Playbooks section not found!")

    # print(f"Printing teams: {teams}")
    return teams


# Step 2: Function to fetch formations and plays for a specific team and side
def get_formations_and_plays(team_name, team_url) -> dict:
    print(f"Fetching data for {team_name} from {team_url}")

    # Make GET request to the team-specific URL (offense/defense)
    response = requests.get(team_url)

    if response.status_code != 200:
        print(f"Error: Could not fetch the playbook.")
        return None
    
    # Parse the page content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the formations (replace this with actual selector for formations)
    formations_section = soup.find('div', class_="mt-5")  # Assuming it's a header
    formations = {}
    formation_links = formations_section.find_all('a', class_='text-xl font-bold text-gray-800')


    for formation_link in formation_links:
        formation_name = formation_link.text.strip()  # Get the formation name (e.g., 'Singleback')
        formation_url = formation_link['href']  # Get the URL of the formation page

        # Initialize the formation entry in the dictionary
        formations[formation_name] = {'url': formation_url, 'plays': []}

        # Now, find the plays associated with this formation.
        # Find the container or section that holds the plays (based on your structure)

        # In this case, it seems each play is inside a <span> tag
        play_spans = formation_link.find_all_next('span', class_='py-2 block font-bold text-sm text-white hover:text-base transition-all duration-200')
        
        for play_span in play_spans:
            play_name = play_span.text.strip()  # Get the play name (e.g., 'Bunch X Nasty')
            formations[formation_name]['plays'].append(play_name)

    return formations


# Step 3: Main function to orchestrate the scraping process
def main():
    # Step 1: Get all teams and their respective pages
    pageData = requests.get(BASE_URL)
    teams = get_team_data(pageData)

    # Step 2: For each team, get the formations and plays
    all_team_data = {}
    for team_name, team_info in teams.items():
        side = team_info['side']
        team_url = team_info['url']

        # Fetch formations and plays for each team
        formations = get_formations_and_plays(team_name, team_url)
        all_team_data[team_name] = {
            'side': side,
            'formations': formations
        }

    # Step 3: Output the final data (you can print, save, or process it further)
    print(all_team_data)


# Run the script
if __name__ == "__main__":
    main()