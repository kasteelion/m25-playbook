import argparse
import requests
from bs4 import BeautifulSoup
import csv

# Function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Scrape playbooks for a specified team and side.')
    parser.add_argument('--team', type=str, required=False, help='The team to scrape playbooks for (e.g., "49ers").')
    parser.add_argument('--side', type=str, required=False, default=None, choices=['offense', 'defense'], help='The side of the ball (offense/defense).')
    return parser.parse_args()

# Function to get the URL for the team-specific playbook page (offense/defense)
def get_team_playbook_url(base_url, team, side) -> str:
    # Construct the team-specific URL based on side (offense/defense)
    return f'{base_url}{team}/{side}/'


# Function to scrape the main playbook page to get the list of teams and their playbooks
def get_teams_playbook_page(base_url):
    response = requests.get(base_url)
    if response.status_code != 200:
        print("Error: Could not fetch the main playbook page.")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all team links from the main playbooks page
    team_links = soup.find_all('div', class_='flex justify-center gap-x-1 flex-row flex-wrap mb-6')
    
    teams = []

    # Iterate through each section (offensive, defensive, etc.)
    for section in team_links:
        # Find all <a> tags inside the current section (each link is a team link)
        anchors = section.find_all('a', href=True)  # Use find_all to get all <a> tags with href
        
        for anchor in anchors:
            # Get the URL from the href attribute of the <a> tag
            team_url = anchor['href']
            
            # Find the <span> tag containing the team name, which should be near the <a> tag
            span = anchor.find_next('span')  # Find the next <span> tag after the <a> tag
            
            if span:
                team_name = span.text.strip()  # Get the team name from the <span> tag
            else:
                team_name = "Unknown Team Name"  # If no <span> tag is found
            
            # Append the (team_name, team_url) tuple to the teams list
            teams.append((team_name, team_url))
    
    return teams

# Function to scrape formations and plays from a team-specific playbook page
def scrape_playbook_page(team_url) -> dict:
    response = requests.get(team_url)
    if response.status_code != 200:
        print(f"Error: Could not fetch the playbook page {team_url}.")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all sections that represent playbooks
    playbook_sections = soup.find_all('div', class_='text-center')
    
    if not playbook_sections:
        print(f"No playbook sections found on {team_url}")
        return None
    
    playbooks = {}
    
    for idx, section in enumerate(playbook_sections, start=1):
        section_name = f"Playbook {idx}"
        playbooks[section_name] = extract_playbook_data(section)
    
    return playbooks

# Function to extract formation and play data from a playbook section
def extract_playbook_data(section):
    formations = {}

    # Find all formation <a> tags within the `section`
    formation_links = section.find_all('a', class_='text-xl font-bold text-gray-800')

    for formation_link in formation_links:
        formation_name = formation_link.text.strip()  # Get the formation name (e.g., 'Singleback')
        formation_url = formation_link['href']  # Get the URL of the formation page

        # Initialize the formation entry in the dictionary
        formations[formation_name] = {'url': formation_url, 'plays': []}

        # Find the plays associated with this formation.
        # In this case, it seems each play is inside a <span> tag
        play_spans = formation_link.find_all_next('span', class_='py-2 block font-bold text-sm text-white hover:text-base transition-all duration-200')
        
        for play_span in play_spans:
            play_name = play_span.text.strip()  # Get the play name (e.g., 'Bunch X Nasty')
            formations[formation_name]['plays'].append(play_name)

    return formations

# Function to write playbook data to CSV
def write_to_csv(playbook_data, csv_file):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        for data in playbook_data:
            writer.writerow(data)

# Main function to drive the scraping
def main():
    args = parse_args()
    base_url = 'https://www.madden-school.com/playbooks/'

    # Get the list of teams and their respective playbook URLs
    teams = get_teams_playbook_page(base_url)

    if not teams:
        print("No teams found.")
        return
    
    # Define CSV file
    csv_file = 'playbooks.csv'
    
    # Add headers if CSV is empty (only once)
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Team', 'Side', 'Playbook', 'Formation', 'Play Name'])
    
    # If a specific team is provided, search for it; otherwise, scrape all teams
    if args.team:
        # Find the team URL based on the user input
        team_name = args.team
        side = args.side if args.side else 'offense'
        
        team_url = None
        for team, team_url_in_list in teams:
            if team_name.lower() in team.lower():  # Case-insensitive match
                team_url = get_team_playbook_url(base_url, team, side)
                print(f"Scraping {side} playbook for {team_name} at {team_url}")
                break
        
        if not team_url:
            print(f"Error: Could not find playbook for {team_name}.")
            return
        
        # Scrape and collect playbooks for the selected team
        playbook_data = []
        playbooks = scrape_playbook_page(team_url)
        
        if playbooks:
            for playbook_name, formations in playbooks.items():
                for formation_name, data in formations.items():
                    for play in data['plays']:
                        playbook_data.append([team_name, side, playbook_name, formation_name, play])
            
            # Write to CSV
            write_to_csv(playbook_data, csv_file)
            print(f"Data for {team_name} has been written to {csv_file}.")
        else:
            print("No playbooks found.")
    else:
        # If no specific team is specified, scrape every team
        for team_name, team_url in teams:
            print(f"\nScraping playbooks for {team_name}...")
            
            for side in ['offense', 'defense']:
                team_url_with_side = get_team_playbook_url(base_url, team_name, side)
                playbooks = scrape_playbook_page(team_url_with_side)
                
                if playbooks:
                    playbook_data = []
                    for playbook_name, formations in playbooks.items():
                        for formation_name, data in formations.items():
                            for play in data['plays']:
                                playbook_data.append([team_name, side, playbook_name, formation_name, play])
                    
                    # Write to CSV
                    write_to_csv(playbook_data, csv_file)
                    print(f"Data for {team_name} ({side}) has been written to {csv_file}.")
                else:
                    print(f"No playbooks found for {side} of {team_name}.")

if __name__ == "__main__":
    main()
