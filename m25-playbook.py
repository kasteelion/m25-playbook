import requests
from bs4 import BeautifulSoup
import pandas as pd

# Send a GET request to the webpage
# url = "https://www.madden-school.com/playbooks/"
url = "https://www.madden-school.com/playbooks/packers/defense/4-3/even-6-1/"
response = requests.get(url)

'''
# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all the playbooks
playbooks = soup.find_all('a')
print(playbooks)

# Create a dictionary to store the playbook information
playbook_info = {}

# Iterate over the playbooks and extract the formation, set, and playbook name
for playbook in playbooks:
    formation = playbook.text.split('>')[1].split('<')[0]
    set_ = playbook.text.split('>')[1].split('<')[0]
    playbook_name = playbook.text.split('>')[1].split('<')[0]
    playbook_info[playbook_name] = {'Formation': formation, 'Set': set_}

# Create a pandas DataFrame from the playbook information
df = pd.DataFrame(playbook_info).T

# Print the DataFrame
print(df)
'''

soup = BeautifulSoup(response.content, 'html.parser')
#print(f"Printing soup {soup}")

target_string = "defense/4-3/even-6-1"
for a in soup.find_all('a'):
    href = a.get('href')
    if href and href.startswith('/playbooks/') and target_string in href:
        print(href)



'''

playbooks = soup.find_all('a', class_='dropdown-item')
print(playbooks)

# Create a dictionary to store the playbook information
playbook_info = {}

# Iterate over the playbooks and extract the formation, set, and playbook name
for playbook in playbooks:
    text = playbook.text.strip()
    parts = text.split(' - ')
    formation = parts[0]
    set_ = parts[1]
    playbook_name = parts[2]
    playbook_info[playbook_name] = {'Formation': formation, 'Set': set_}

# Create a pandas DataFrame from the playbook information
df = pd.DataFrame(playbook_info).T

# Print the DataFrame
print(df)
'''