from zenrows import ZenRowsClient
import pandas as pd
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# ZenRows API setup
# Get the ZenRows API key from the environment
api_key = os.getenv("ZENROWS_API_KEY")
client = ZenRowsClient(api_key)

# File to store the last processed code
last_processed_file = "last_processed_code.txt"

# Excel file to store the names
output_file = "ufind_catalog_names.xlsx"

# Function to get the list of names from a given URL using ZenRows
def get_names_from_page(url):
    # Use ZenRows to fetch the page with JavaScript rendering enabled
    params = {"js_render": "true"}  # Enable JavaScript rendering
    response = client.get(url, params=params)

    # Check if the page exists (200 OK status), otherwise return None
    if response.status_code == 404:
        return None  # Return None if the page doesn't exist

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the name elements on the page
    names_data = []
    
    # Find all div elements that contain the names
    for div in soup.select('.clearfix.container-fluid'):
        # Extract the name
        name_element = div.find('a', class_='h3')
        name_text = name_element.get_text().strip() if name_element else "N/A"

        # Append the extracted name to the list
        names_data.append([name_text])

    return names_data

# Function to save the data to the Excel file after each iteration
def save_to_excel(data, output_file):
    # Try to load existing data if the file already exists
    try:
        df_existing = pd.read_excel(output_file)
        # Use pd.concat to append new data to existing data
        data_df = pd.DataFrame(data, columns=['Name'])
        df = pd.concat([df_existing, data_df], ignore_index=True)
    except FileNotFoundError:
        # If file doesn't exist, create a new dataframe
        df = pd.DataFrame(data, columns=['Name'])

    # Save the updated dataframe to Excel
    df.to_excel(output_file, index=False)

# Function to get the last processed code from file
def get_last_processed_code():
    try:
        with open(last_processed_file, 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        return None

# Function to save the last processed code to file
def save_last_processed_code(code):
    with open(last_processed_file, 'w') as file:
        file.write(code)

# Get the last processed code (if available)
last_processed_code = get_last_processed_code()

# Determine where to start
start_letter = 'A'
start_page = 1

if last_processed_code:
    # Parse the last processed code, e.g., 'A-1'
    start_letter, start_page = last_processed_code.split('-')
    start_page = int(start_page) + 1  # Start from the next page

# Loop through the letters A to Z, starting from the correct letter
for letter in range(ord(start_letter), ord('Z') + 1):
    current_letter = chr(letter)

    # Start with the correct page number and continue until we get a 404
    page_number = start_page if letter == ord(start_letter) else 1

    while True:
        # Create the URL for the current page
        code = f"{current_letter}-{page_number}"
        url = f"https://ufind.name/catalog-{code}"
        print(f"Fetching: {url}")

        # Fetch the names from the current page using ZenRows
        names_data = get_names_from_page(url)

        # If the page doesn't exist, break out of the loop for this letter
        if names_data is None:
            print(f"Page not found: {url}. Moving to next letter...")
            break

        # Save the data for this page to the Excel file
        save_to_excel(names_data, output_file)
        print(f"Data from {url} saved to {output_file}")

        # Save the last processed code
        save_last_processed_code(code)

        # Increment the page number
        page_number += 1

        # Sleep to avoid overwhelming the server
        time.sleep(2)

    # Reset start_page for the next letter
    start_page = 1

print(f"Scraping complete. Data saved to {output_file}")
