import time
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright

# Load environment variables from .env file
load_dotenv()

# Base URL for the website
base_url = "https://ufind.name"

# File to store the last processed name
last_processed_file = "last_processed_name.txt"
# Excel file to store the data from names
names_file = "ufind_catalog_names.xlsx"  # This is the Excel file from the previous script
# Excel file to store the scraped data
output_file = "scraped_data.xlsx"

# Function to get the last processed name from file
def get_last_processed_name():
    try:
        with open(last_processed_file, 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        return None

# Function to save the last processed name to file
def save_last_processed_name(name):
    with open(last_processed_file, 'w') as file:
        file.write(name)

# Function to load names from the Excel file
def load_names_from_excel(names_file):
    try:
        df = pd.read_excel(names_file)
        return df['Name'].tolist()  # Convert the 'Name' column to a list
    except FileNotFoundError:
        print(f"File {names_file} not found.")
        return []

# Check if there's a previously saved name and resume from it
last_processed_name = get_last_processed_name()

# Load the names from the Excel file
names_list = load_names_from_excel(names_file)

# Initialize to start after the last processed name, if available
started = False if last_processed_name else True

# Try to load existing data if the file already exists
try:
    df = pd.read_excel(output_file)
    results = df.values.tolist()  # Convert dataframe back to list
except FileNotFoundError:
    results = []

# Function to scrape the data using Playwright
def scrape_data_using_playwright(name, page):
    # Create the search URL
    search_url = f"{base_url}/{name.replace(' ', '+')}"

    # Use Playwright to navigate to the search URL
    page.goto(search_url)

    # Wait for the content to load (adjust the wait time if necessary)
    time.sleep(2)

    # Get the page content and parse it using BeautifulSoup
    html_content = page.content()
    soup = BeautifulSoup(html_content, 'html.parser')

    # Check if the title is "Just a moment...", indicating Cloudflare bot protection
    title = soup.find('title')
    if title and title.get_text() == "Just a moment...":
        print("Cloudflare bot detection triggered. Update the CLOUDFLARE_CLEARANCE_COOKIE cookie")
        exit(1)  # Exit the program with a non-zero status code

    # Extract the relevant data
    rows = soup.select('#tblCars .row')
    
    data = []
    for row in rows:
        # Extract the relevant fields for each person (name, address, phone, car model, and VIN)
        person_name = row.find('strong', class_='nm').text.strip() if row.find('strong', class_='nm') else ""
        address = row.find('span', class_='home').text.strip() if row.find('span', class_='home') else ""
        phone = row.find('span', class_='tel').text.strip() if row.find('span', class_='tel') else ""
        car_model = row.find('span', class_='car').text.strip() if row.find('span', class_='car') else ""
        vin = row.find('span', class_='vin').text.strip() if row.find('span', class_='vin') else ""

        # Append the extracted data to the list
        data.append([person_name, address, phone, car_model, vin])

    return data

# Start Playwright and scrape data
with sync_playwright() as p:
    # Launch browser (you can choose between chromium, firefox, or webkit)
    browser = p.chromium.launch(headless=False)  # Set headless=True for headless mode
    context = browser.new_context()

    cf_cookie = os.getenv("CLOUDFLARE_CLEARANCE_COOKIE")

    # Add Cloudflare clearance cookie to the context
    context.add_cookies([{
        "name": "cf_clearance",  # Cloudflare clearance cookie name
        "value": cf_cookie,  # Replace with actual value
        "domain": "ufind.name",  # Domain for which the cookie is valid
        "path": "/",  # Path of the cookie
        "expires": -1,  # -1 means the cookie doesn't expire
        "httpOnly": True,
        "secure": True,
        "sameSite": "Strict"
    }])

    # Open a new page in the browser
    page = context.new_page()

    # Iterate through the list of names
    for name in names_list:
        # Skip until the last processed name is found (if applicable)
        if not started:
            if name == last_processed_name:
                # We found the last processed name, so we can start processing the next one
                started = True
            continue

        try:
            # Scrape the data for the current name
            print(f"Fetching data for: {name}")
            name_data = scrape_data_using_playwright(name, page)

            if not name_data:
                print(f"Cars Data not found for : {name}. Moving to next name...")
                continue

            # Append the scraped data to results
            results.extend(name_data)

            # Save the data to the Excel file after processing each name
            df = pd.DataFrame(results, columns=['Name', 'Address', 'Phone', 'Car Model', 'VIN'])
            df.to_excel(output_file, index=False)
            print(f"Successfully processed: {name}")

        except Exception as e:
            print(f"Error extracting data for {name}: {e}")

        # Now that the name has been processed, save it as the last processed name
        save_last_processed_name(name)

        # Sleep for a few seconds to avoid overwhelming the server
        time.sleep(5)

    # Close the browser when done
    browser.close()

print(f"Scraping complete. Data saved to {output_file}")
