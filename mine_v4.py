import argparse
import requests
from bs4 import BeautifulSoup
import csv


# Function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Scrape playbook data for a specific team and side (offense/defense).")
    
    # Use '--team' flag to specify the team
    parser.add_argument('--team', required=True, help='The team name (e.g., "49ers", "Ravens")')

    # Use '--side' flag to specify offense/defense, with 'offense' as the default
    parser.add_argument('--side', choices=['offense', 'defense'], default='offense', help='The side to scrape (offense or defense). Default is offense.')
    
    return parser.parse_args()

# Function to get the URL for the team-specific playbook page (offense/defense)
def get_team_playbook_url(base_url, team, side) -> str:
    # Construct the team-specific URL based on side (offense/defense)
    return f'{base_url}{team}/{side}/'



# Function to get all available teams from the main playbook page
def get_teams_playbook_page(base_url):
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Error: Could not fetch the main playbook page {base_url}.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all team links (team names are inside <a> tags with no specific class but are enclosed in spans)
    team_links = soup.find_all('a', href=True)

    teams = []
    for link in team_links:
        # Extract the team name (assuming the team name is in the span element)
        team_name = link.find('span')
        if team_name:
            team_name = team_name.text.strip()
            print(repr(team_name))
            teams.append(team_name)

    return teams


def scrape_playbook_page(team_name, base_url, side):
    team_url = get_team_playbook_url(base_url, team_name, side)
    response = requests.get(team_url)
    
    if response.status_code != 200:
        print(f"Error: Could not fetch the playbook page {team_url}.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all sections that represent playbooks (like offensive/defensive sections)
    playbook_sections = soup.find_all('div', class_='text-center')
    print(f"Found {len(playbook_sections)} playbook sections")

    playbook_data = []

    # Loop through each playbook section (offense/defense)
    for section in playbook_sections:
        # Extract formations (these should be inside <a> tags)
        formation_links = section.find_all('a', class_='text-xl font-bold text-gray-800')
        
        print(f"Found {len(formation_links)} formation links in section")

        for formation_link in formation_links:
            formation_name = formation_link.text.strip()
            formation_url = formation_link['href']

            # Construct full URL for the formation page
            formation_full_url = "https://www.madden-school.com" + formation_url
            print(f"Formation: {formation_name}, URL: {formation_full_url}")

            # Scrape the sets for this formation (go to the formation page)
            formation_response = requests.get(formation_full_url)
            if formation_response.status_code != 200:
                print(f"Error: Could not fetch the formation page {formation_full_url}.")
                continue

            formation_soup = BeautifulSoup(formation_response.text, 'html.parser')
            
            # Now look for set links (sets are inside specific divs like the ones you've seen)
            set_spans = formation_soup.find_all('div', class_='flex flex-wrap justify-center -mx-2')
            #set_spans_to_find = formation_soup.find_all('span', class_="py-2 block font-bold text-sm text-white hover:text-base transition-all duration-200")
            


            print(f"Found {len(set_spans)} set spans in formation")

            # Loop through each set span to find the set names and URLs
            for set_span in set_spans:
                set_name = set_span.find('span', class_="py-2 block font-bold text-sm text-white hover:text-base transition-all duration-200").text.strip()
                #set_name = set_name.replace("\n", "").replace("\r", "")
                
                print(repr(set_name))
                
                set_url = set_span.find('a')['href'] if set_span.find('a') else None



                #print(f"Set: {set_name}")
                #print(f"Set URL: {set_url}")

                if set_url:
                    # Construct full URL for the set
                    set_full_url = "https://www.madden-school.com" + set_url
                    #print(f"Set URL (full): {set_full_url}")

                    # Scrape plays for this set (if set_url exists)
                    plays = scrape_plays_for_set(set_full_url)
                    #print(f"Found {len(plays)} plays for set {set_name}")
                    #set_name = set_span.find_all('span', class="py-2 block font-bold text-sm text-white hover:text-base transition-all duration-200")

                    # Add the row data for each play in this set
                    for play_name in plays:
                        playbook_data.append([team_name, side, formation_name, set_name, play_name])

    return playbook_data


def scrape_plays_for_set(set_url):
    """Function to scrape plays for a specific set given its URL."""
    response = requests.get(set_url)
    if response.status_code != 200:
        print(f"Error: Could not fetch set page {set_url}.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find play names by looking for divs that hold play names
    play_divs = soup.find_all('div', class_='m-1.5')
    print(f"Found {len(play_divs)} play divs under set URL: {set_url}")

    play_names = []
    for div in play_divs:
        play_name_div = div.find('div', class_='py-2 text-center w-full h-10 block font-bold text-sm text-white hover:text-[16px] hover:text-white')
        if play_name_div:
            play_name = play_name_div.text.strip()
            # print(repr(play_name))
            
            play_names.append(play_name)

    return play_names


# Function to write the data to a CSV file
def write_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Team", "Side", "Formation", "Set", "Play"])
        for row in data:
            writer.writerow(row)


def main():
    # Parse the command-line arguments
    args = parse_args()

    base_url = 'https://www.madden-school.com/playbooks/'
    
    # Get the list of teams from the main playbook page
    teams = get_teams_playbook_page(base_url)

    # Look for the team specified in the arguments
    team_url = None
    for team_name in teams:
        if args.team.lower() in team_name.lower():  # Case-insensitive match
            team_url = get_team_playbook_url(base_url, team_name, args.side)
            print(f"Scraping {args.side} playbook for {team_name} at {team_url}")
            break
    
    if not team_url:
        print(f"Error: Could not find playbook for team '{args.team}'")
    else:
        # Scrape the playbook data for the selected team and side
        playbook_data = scrape_playbook_page(args.team, base_url, args.side)
        

        # Write the data to a CSV file
        if playbook_data:
            write_to_csv(playbook_data, 'playbook_data.csv')
            print(f"Playbook data for {args.team} ({args.side}) has been written to 'playbook_data.csv'.")
        else:
            print(f"No playbook data found for {args.team} ({args.side}).")




if __name__ == "__main__":
    main()