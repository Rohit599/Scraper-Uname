import time
import pandas as pd
from bs4 import BeautifulSoup
from zenrows import ZenRowsClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# ZenRows API setup
# Get the ZenRows API key from the environment
api_key = os.getenv("ZENROWS_API_KEY")
client = ZenRowsClient(api_key)
base_url = "https://ufind.name/"

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

# Iterate through the list of names
for name in names_list:

    # Skip until the last processed name is found (if applicable)
    if not started:
        if name == last_processed_name:
            # We found the last processed name, so we can start processing the next one
            started = True
        continue

    # Make a request to ZenRows to fetch the page content for the current name
    search_url = f"{base_url}/{name.replace(' ', '+')}"
    params = {"js_render": "true"}  # Enable JavaScript rendering
    response = client.get(search_url, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch data for {name}. Status code: {response.status_code}")
        continue

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # Find all rows in the car information table
        rows = soup.select('#tblCars .row')
        
        for row in rows:
            # Extract the relevant fields for each person (name, address, phone, car model, and VIN)
            person_name = row.find('strong', class_='nm').text.strip() if row.find('strong', class_='nm') else ""
            address = row.find('span', class_='home').text.strip() if row.find('span', class_='home') else ""
            phone = row.find('span', class_='tel').text.strip() if row.find('span', class_='tel') else ""
            car_model = row.find('span', class_='car').text.strip() if row.find('span', class_='car') else ""
            vin = row.find('span', class_='vin').text.strip() if row.find('span', class_='vin') else ""
            
            # Append the extracted data to the results list
            results.append([person_name, address, phone, car_model, vin])

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
