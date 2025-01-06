# Madden 25 Playbook Finder
## Requirements
- Python >= 3.11
- requests
- bs4

## Installation
```plaintext
pip install requests bs4
```

## Basic Usage
`python3 m25-playbook.py --team 49ers --side defense`

This will pull the 49ers defensive plays from [Madden School](https://www.madden-school.com/playbooks/) and will return the information found to the terminal.

## Exporting All Information
`python3 m25-playbook.py --exportall`