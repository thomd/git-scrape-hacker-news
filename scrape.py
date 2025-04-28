import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

# URL of the page to scrape
url = "https://news.ycombinator.com/"

# Fetch the page
response = requests.get(url)
response.raise_for_status()

# Parse the page
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the main submission rows
items = soup.find_all('tr', class_='athing')

# Get current scraping datetime
scrape_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
scrape_time_for_filename = scrape_time.replace(':', '-').replace(' ', '_')

# Prepare CSV output
rows = []

for item in items:
    # ID (from item id attribute)
    item_id = item.get('id')

    # Rank
    rank_tag = item.find('span', class_='rank')
    rank = int(rank_tag.text.strip('.')) if rank_tag else None

    # Title and URL
    titleline = item.find('span', class_='titleline')
    if titleline and titleline.a:
        title = titleline.a.text
        url_link = titleline.a['href']

        # Fix relative URLs
        if url_link.startswith('item?id='):
            url_link = 'https://news.ycombinator.com/' + url_link
    else:
        title = ''
        url_link = ''

    # Find subtext
    subtext = item.find_next_sibling('tr').find('td', class_='subtext')

    if subtext:
        # Points
        score_tag = subtext.find('span', class_='score')
        points = int(score_tag.text.replace(' points', '')) if score_tag else 0

        # Comments and check comment link
        comment_links = subtext.find_all('a')
        comments_text = comment_links[-1].text if comment_links else ''
        comments = 0
        if 'comment' in comments_text:
            comments = int(comments_text.split()[0].replace('\xa0', ''))
    else:
        points = 0
        comments = 0

    # Append the row
    rows.append([item_id, rank, title, url_link, points, comments, scrape_time])

# Create 'data' directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Define output filename inside the 'data' folder
output_filename = os.path.join('data', f'hacker_news_scrape_{scrape_time_for_filename}.csv')

# Write to CSV
with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

    # Write header
    writer.writerow(["id", "rank", "title", "url", "points", "comments", "scrape-date"])

    # Write the data rows
    for row in rows:
        writer.writerow(row)

print(f"Scraped {len(rows)} stories.")
print(f"Data successfully written to {output_filename}")

