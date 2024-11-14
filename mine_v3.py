import argparse
import requests
from bs4 import BeautifulSoup

# Function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Scrape playbooks for a specified team and side.')
    parser.add_argument('--team', type=str, required=True, help='The team to scrape playbooks for (e.g., "49ers").')
    parser.add_argument('--side', type=str, required=False, default='offense', choices=['offense', 'defense'], help='The side of the ball (offense/defense).')
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
    #print(soup.prettify())
    
    # Find all team links from the main playbooks page
    team_links = soup.find_all('div', class_='flex justify-center gap-x-1 flex-row flex-wrap mb-6')
    #print(team_links)


    teams = []

    # Iterate through each section (offensive, defensive, etc.)
    for section in team_links:
        # Find all <a> tags inside the current section (each link is a team link)
        anchors = section.find_all('a', href=True)  # Use find_all to get all <a> tags with href
        
        for anchor in anchors:
            # Get the URL from the href attribute of the <a> tag
            team_url = anchor['href']
            
            # Now, find the <span> tag containing the team name, which should be near the <a> tag
            span = anchor.find_next('span')  # Find the next <span> tag after the <a> tag
            
            if span:
                team_name = span.text.strip()  # Get the team name from the <span> tag
            else:
                team_name = "Unknown Team Name"  # If no <span> tag is found
            
            # Append the (team_name, team_url) tuple to the teams list
            teams.append((team_name, team_url))
    
    #print(f"List of teams {teams}")
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
    #print(playbook_sections)
    
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

        # Now, find the plays associated with this formation.
        # In this case, it seems each play is inside a <span> tag
        play_spans = formation_link.find_all_next('span', class_='py-2 block font-bold text-sm text-white hover:text-base transition-all duration-200')
        
        for play_span in play_spans:
            play_name = play_span.text.strip()  # Get the play name (e.g., 'Bunch X Nasty')
            formations[formation_name]['plays'].append(play_name)

    return formations

# Main function to drive the scraping
def main():
    args = parse_args()
    base_url = 'https://www.madden-school.com/playbooks/'

    # Get the list of teams and their respective playbook URLs
    teams = get_teams_playbook_page(base_url)

 
    # if teams:
    #     print(f"Found {len(teams)} teams:")
    #     # for team_name, team_url in teams:
    #     #     print(f"Team: {team_name}, URL: {team_url}")
    # else:
    #     print("No teams found.")
    
    # Find the team the user requested and scrape its playbook
    team_name = args.team
    side = args.side

    
    # Look for the team URL
    team_url = None
    for team, team_url_in_list in teams:
        if team_name.lower() in team.lower():  # Case-insensitive match
            team_url = get_team_playbook_url(base_url, team, side)
            print(f"Searching inside of {team_url}")
            break

    if team_url is None:
        print(f"Error: Could not find playbook for the {team_name}.")
        return


    print(f"Scraping {side} playbook for the {team_name}...")
    

    # Function to scrape formations and plays from a team-specific playbook page
    playbooks = scrape_playbook_page(team_url)
    
    # Print playbooks for debugging purposes. This 
    # print(playbooks)

    if playbooks:
        # Print the playbooks and their respective formations and plays
        for playbook_name, formations in playbooks.items():
            print(f"\n{playbook_name}:")
            for formation_name, data in formations.items():
                print(f"  Formation: {formation_name} (URL: {data['url']})")
                print("  Plays:")
                for play in data['plays']:
                    print(f"    - {play}")
            print()


if __name__ == "__main__":
    main()
