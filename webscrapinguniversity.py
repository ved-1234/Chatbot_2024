
import requests
from bs4 import BeautifulSoup

# List of URLs to fetch data from
urls = [
    "https://mu.ac.in/",
    "https://mu.ac.in/examination",
    "https://mu.ac.in/commerce-management",
    "https://mu.ac.in/#",
    "https://mu.ac.in/#sec-gallery",
    "https://mu.ac.in/facilities",
    "https://academicaudit.mu.ac.in/AA/college_reps.php"
]

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

# Open a file to write the text content with UTF-8 encoding
with open("data.txt", "w", encoding='utf-8') as f:
    # Loop through each URL
    for url in urls:
        try:
            # Fetch the content of the URL
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check if the request was successful

            # Parse the content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Write the text content to the file
            f.write(f"Content from {url}:\n")
            f.write(soup.get_text())
            f.write("\n" + "="*80 + "\n")

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")


