"""
Clean Traveler & Travel Records
Author: Olusoji Matthew
Description: Cleans raw CSV data for travelers and travel records, making it ready for use in the GUI app.
"""

import pandas as pd
import os

# ------------------------------
# File paths (change if needed)
# ------------------------------
travelers_file = "travelers.csv"
travels_file = "travels.csv"

cleaned_travelers_file = "travelers_cleaned.csv"
cleaned_travels_file = "travels_cleaned.csv"

# ------------------------------
# Load CSVs
# ------------------------------
if not os.path.exists(travelers_file) or not os.path.exists(travels_file):
    print("Error: travelers.csv or travels.csv not found in the current directory.")
    exit(1)

travelers = pd.read_csv(travelers_file)
travels = pd.read_csv(travels_file)

print(f"Loaded {len(travelers)} travelers and {len(travels)} travel records.")

# ------------------------------
# Clean Travelers Data
# ------------------------------
# Remove duplicate travelers
travelers = travelers.drop_duplicates(subset=['traveler_id', 'email'])

# Fill missing values
travelers['name'] = travelers['name'].fillna('Unknown').str.title()
travelers['email'] = travelers['email'].fillna('unknown@example.com')
travelers['phone'] = travelers['phone'].fillna('Unknown')
travelers['passport_number'] = travelers['passport_number'].fillna('Unknown')

# ------------------------------
# Clean Travels Data
# ------------------------------
# Remove duplicate travel records
travels = travels.drop_duplicates(subset=['travel_id'])

# Fill missing text values
travels['destination'] = travels['destination'].fillna('Unknown').str.title()
travels['purpose'] = travels['purpose'].fillna('Unknown').str.capitalize()

# Convert dates
travels['departure_date'] = pd.to_datetime(travels['departure_date'], errors='coerce')
travels['return_date'] = pd.to_datetime(travels['return_date'], errors='coerce')

# Remove rows with invalid dates
travels = travels.dropna(subset=['departure_date', 'return_date'])

# Optional: ensure return_date >= departure_date
travels = travels[travels['return_date'] >= travels['departure_date']]

# ------------------------------
# Sort Travels by Traveler and Departure Date
# ------------------------------
travels = travels.sort_values(by=['traveler_id', 'departure_date'])

# ------------------------------
# Save Cleaned CSVs
# ------------------------------
travelers.to_csv(cleaned_travelers_file, index=False)
travels.to_csv(cleaned_travels_file, index=False)

print(f"Cleaned travelers saved to: {cleaned_travelers_file}")
print(f"Cleaned travel records saved to: {cleaned_travels_file}")
print("Data cleaning completed successfully!")
