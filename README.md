# EV Chargers Atlanta MSA Analysis
## Overview
This project processes electric vehicle (EV) charging station data and calculates the total number of chargers installed within the Atlanta Metropolitan Statistical Area (MSA). It filters raw CSV data, cleans it, and aggregates charger counts by type.

## Features
- Loads EV charging station data from a CSV file
- Cleans and standardizes city names
- Filters data to only include Atlanta MSA cities
- Handles missing values in charger counts
- Computes totals for:
  - Level 1 EV chargers
  - Level 2 EV chargers
  - DC Fast chargers
  - Outputs total charger counts for the region

## Technologies Used
- Python 3
- Pandas

## Input Data
- The script expects a CSV file containing at least the following columns:
  - City
  - EV Level1 EVSE Num
  - EV Level2 EVSE Num
  - EV DC Fast Count

## How It Works
- Reads the CSV file using pandas
- Filters relevant columns
- Standardizes city names (strip + title case)
- Filters rows to only Atlanta MSA cities
- Replaces missing charger values with 0
- Converts values to integers
- Sums charger counts by type and overall total
