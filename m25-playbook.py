import requests
from bs4 import BeautifulSoup
import pandas as pd

# Send a GET request to the webpage
# url = "https://www.madden-school.com/playbooks/"
url1 = "https://www.madden-school.com/playbooks/"
teamResponse = requests.get(url1)

soup = BeautifulSoup(teamResponse.content, 'html.parser')
#print(f"Printing soup {soup}")

target_string = "playbooks"
exclude_strings = ["finder", "search"]


# Find teams or playbooks
for a in soup.find_all('a'):
    # Getting all hrefs
    href = a.get('href')

    # Filtering for playbooks
    if href and href.startswith('/playbooks/') and target_string in href:
            
        # Exclude anything that isn't a playbook
        if any(exclude_str in href for exclude_str in exclude_strings):
            continue  # Skip this iteration if an exclude string is found
        
        url_parts = href.split('/')
        teamAndSide = '/'.join(url_parts[2:])
        # print(f"URL is: {teamAndSide}")
        
url2 = "https://www.madden-school.com/playbooks/{teamandside}"
teamResponse = requests.get(url2)
for a in soup.find_all('a'):
    # Getting all hrefs
    href = a.get('href')

    # Filtering for playbooks
    if href and href.startswith('/playbooks/') and target_string in href:
            
        # Exclude anything that isn't a playbook
        if any(exclude_str in href for exclude_str in exclude_strings):
            continue  # Skip this iteration if an exclude string is found
        
        url_parts2 = href.split('/')
        formations = '/'.join(url_parts2[3:])
        # print(f"URL is: {teamAndSide}")
        print(url_parts2)
        
"""
# Send a GET request to the webpage
# url = "https://www.madden-school.com/playbooks/"
url = "https://www.madden-school.com/playbooks/packers/defense/4-3/even-6-1/"
setResponse = requests.get(url)


soup = BeautifulSoup(setResponse.content, 'html.parser')
#print(f"Printing soup {soup}")

# Create an list for teams
teams = []



target_string = "defense" or "offense"

for a in soup.find_all('a'):
    href = a.get('href')
    amountOfSlashes = href.count('/')
    amountOfSlashes -= 1
    
    if href and href.startswith('/playbooks/') and (amountOfSlashes == 6) and target_string in href:
       url_parts = href.split('/')
       thingwewant = ','.join(url_parts[4:])
       print(f"URL is: {thingwewant}")
"""
