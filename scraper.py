import hashlib
import os
import requests


# Function to check if a cached HTML file exists
def get_cached_html(url):
    # Create a hash of the URL to name the file
    url_hash = hashlib.md5(url.encode()).hexdigest()
    file_path = os.path.join("reqs", f"{url_hash}.html")

    print(f"Hashing URL: {url} -> MD5 Hash: {url_hash}")
    
    # If the file exists, read it
    if os.path.exists(file_path):
        print(f"Using cached HTML for {url}")
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    return None


# Function to fetch HTML content from a URL (either from cache or network)
def fetch_html(url):
    # Try to get the cached HTML first
    cached_html = get_cached_html(url)
    if cached_html:
        return cached_html
    
    # If not cached, make a request to fetch the content
    response = requests.get(url)
    if response.status_code == 200:
        save_html(url, response.text)  # Cache the response
        return response.text
    else:
        print(f"Error fetching {url}: {response.status_code}")


# Function to save the HTML response to a local file
def save_html(url, html_content):
    # Create a hash of the URL to name the file
    url_hash = hashlib.md5(url.encode()).hexdigest()
    print(f"Data not hashed!!\nHashing URL: {url} -> MD5 Hash: {url_hash}\n")
    os.makedirs("reqs", exist_ok=True)  # Create 'reqs' directory if not exists
    file_path = os.path.join("reqs", f"{url_hash}.html")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"Saved HTML content for {url} to {file_path}")