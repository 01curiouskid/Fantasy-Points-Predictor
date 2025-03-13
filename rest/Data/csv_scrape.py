import csv
import os
import pandas as pd  # Import pandas for reading existing CSV data
import requests
from bs4 import BeautifulSoup
import re
import time

# File paths
csv_file = "Datasets/people.csv"
output_file = "players_data_new.csv"

# Check if the output file already exists
if not os.path.exists(output_file):
    # Create the file and write the header if it doesn't exist
    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "player_id",
            "names",
            "role",
            "batting_style",
            "bowling_style",
            "image",
        ])

# Read existing data from the output file to avoid duplicates
try:
    existing_data = pd.read_csv(output_file)  # Using pandas to read the file
    processed_ids = set(existing_data["player_id"].astype(str))  # Convert to set of processed IDs
except FileNotFoundError:
    processed_ids = set()  # Initialize an empty set if file not found

# Function to fetch player details
def fetch_player_details(player_name):
    try:
        search_url = f"https://www.google.com/search?q={player_name}%20cricbuzz"
        response = requests.get(search_url, timeout=10)
        search_page = BeautifulSoup(response.text, "lxml")
        link_div = search_page.find("div", class_="kCrYT")
        if not link_div:
            return None, None, None, None

        link = link_div.find("a", href=re.compile(r"[/]([a-z]|[A-Z])\w+"))
        if not link:
            return None, None, None, None

        cricbuzz_url = link["href"][7:]  # Remove '/url?q=' prefix
        cricbuzz_response = requests.get(cricbuzz_url, timeout=10).text
        cricbuzz_page = BeautifulSoup(cricbuzz_response, "lxml")

        profile_section = cricbuzz_page.find("div", class_="cb-col cb-col-100 cb-bg-grey")
        if not profile_section:
            return None, None, None, None

        # Extract data
        role = profile_section.find("div", text="Role").find_next_sibling("div").text.strip() if profile_section.find("div", text="Role") else None
        batting_style = profile_section.find("div", text="Batting Style").find_next_sibling("div").text.strip() if profile_section.find("div", text="Batting Style") else None
        bowling_style = profile_section.find("div", text="Bowling Style").find_next_sibling("div").text.strip() if profile_section.find("div", text="Bowling Style") else None
        image = cricbuzz_page.find("img", {"title": "profile image"})["src"] if cricbuzz_page.find("img", {"title": "profile image"}) else None

        return role, batting_style, bowling_style, image
    except Exception as e:
        print(f"Error fetching data for {player_name}: {e}")
        return None, None, None, None

# Read input CSV and process players
with open(csv_file, mode="r") as infile:
    reader = csv.reader(infile)
    next(reader)  # Skip header
    for player_id, name in reader:
        if player_id in processed_ids:  # Skip already processed players
            continue

        print(f"Processing player: {name} (ID: {player_id})")
        role, batting_style, bowling_style, image = fetch_player_details(name)

        # Append the new data to the output file
        with open(output_file, mode="a", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow([player_id, name, role, batting_style, bowling_style, image])

        # Delay to prevent rate-limiting
        time.sleep(2)

print("Data collection completed.")
