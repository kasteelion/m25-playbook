import requests
from bs4 import BeautifulSoup
import pandas as pd

# Send a GET request to the webpage
# url = "https://www.madden-school.com/playbooks/"
url = "https://www.madden-school.com/playbooks/packers/defense/4-3/even-6-1/"
response = requests.get(url)


soup = BeautifulSoup(response.content, 'html.parser')
#print(f"Printing soup {soup}")



target_string = "defense/4-3/even-6-1"

for a in soup.find_all('a'):
    href = a.get('href')
    amountOfSlashes = href.count('/')
    amountOfSlashes -= 1
    
    if href and href.startswith('/playbooks/') and (amountOfSlashes == 6) and target_string in href:
       url_parts = href.split('/')
       thingwewant = '/'.join(url_parts[4:])
       print(f"URL is: {thingwewant}")
