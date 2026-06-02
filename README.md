# EV Chargers Atlanta MSA Analysis
## Overview
This project processes electric vehicle (EV) charging station data and calculates the total number of chargers installed within the Atlanta Metropolitan Statistical Area (MSA). The script filters raw CSV data, cleans and standardizes values, handles missing data, and aggregates charger counts by charger type and access type.

## Features
- Loads EV charging station data from a CSV file
- Handles common file-reading errors:
  - Missing file
  - Empty file
  - CSV parsing errors
- Cleans and standardizes city names
- Filters data to only include Atlanta MSA cities
- Cleans and standardizes Access Code values
- Handles missing charger counts by replacing null values with 0
- Converts charger counts to integers
- Computes totals for:
  - Level 1 EV chargers
  - Level 2 EV chargers
  - DC Fast chargers
  - Total EV chargers installed
- Aggregates charger counts by Access Code
- Returns a cleaned pandas DataFrame for further analysis

## Technologies Used
- Python 3
- Pandas

## Input Data
- The script expects a CSV file containing at least the following columns:
  - City
  - EV Level1 EVSE Num
  - EV Level2 EVSE Num
  - EV DC Fast Count
  - Access Code

## Usage
- Download the "EV Charging Ports" CSV file from [https://afdc.energy.gov/stations#/analyze?region=US-GA&country=US&access=public&access=private&fuel=BD&fuel=CNG&fuel=E85&fuel=HY&fuel=LNG&fuel=LPG&fuel=ELEC&fuel=RD&lpg_secondary=true&hy_nonretail=true&ev_levels=all&tab=station](url)
- Place the CSV file in the same folder as your Python script.
- If needed, replace the filename at the end of the script: print(ev_chargers_data("alt_fuel_stations_ev_charging_units (Jun 2 2026).csv"))
- Run the script: python ev_chargers.py
