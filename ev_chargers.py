import pandas as pd

atlanta_msa_cities = [
    "Acworth", "Adairsville", "Aldora", "Alpharetta", "Atlanta",
    "Auburn", "Austell", "Avondale Estates", "Ball Ground",
    "Berkeley Lake", "Bethlehem", "Between", "Bostwick", "Bowdon",
    "Braselton", "Braswell", "Bremen", "Brookhaven", "Brooks",
    "Buchanan", "Buckhead", "Buford", "Canton", "Carl",
    "Carrollton", "Cartersville", "Centralhatchee", "Chamblee",
    "Chattahoochee Hills", "Clarkston", "College Park", "Concord",
    "Conyers", "Covington", "Cumming", "Dacula", "Dahlonega",
    "Dallas", "Dawsonville", "Decatur", "Doraville", "Douglasville",
    "Duluth", "Dunwoody", "East Point", "Emerson", "Ephesus",
    "Euharlee", "Fairburn", "Fayetteville", "Flovilla",
    "Forest Park", "Franklin", "Milton", "Mulberry", "Newnan", "Roswell",
    "Sandy Springs", "Smyrna", "Snellville", "South Fulton",
    "Stockbridge", "Stone Mountain", "Stonecrest", "Suwanee",
    "Tucker", "Union City", "Villa Rica", "Woodstock"]

def ev_chargers_data(file_path):
    # Reads CSV file
    try:
        ev_chargers_df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return None
    except pd.errors.ParserError:
        print("Error: There was a parsing error while reading the file.")
        return None
    
    # Check for required columns and keep only those needed for analysis
    columns_to_keep = ['City', 'EV Level1 EVSE Num', 'EV Level2 EVSE Num', 'EV DC Fast Count', 'Access Code'] 
    # could be nice to have these columns if needed: 'Date Last Confirmed', 'Updated At', 'Access Detail Code'
    
    missing_cols = [col for col in columns_to_keep if col not in ev_chargers_df.columns] 
    if missing_cols:
        print(f"Missing columns: {missing_cols}")
    ev_chargers_df = ev_chargers_df[columns_to_keep]

    # Clean and filter data for Atlanta MSA cities
    ev_chargers_df['City'] = ev_chargers_df['City'].fillna('').str.strip().str.title()
    ev_chargers_df = ev_chargers_df[ev_chargers_df['City'].isin(atlanta_msa_cities)]

    # Clean 'Access Code' column and fill missing values with 'Unknown'
    ev_chargers_df['Access Code'] = ev_chargers_df['Access Code'].fillna('Unknown').str.strip().str.title().astype(str)
    
    # Fill missing values in charger count columns with 0 and convert to integers
    charger_columns = ['EV Level1 EVSE Num', 'EV Level2 EVSE Num', 'EV DC Fast Count']
    ev_chargers_df[charger_columns] = ev_chargers_df[charger_columns].fillna(0).astype(int)
    
    # Calculate total chargers by type and overall total
    level_1_count = int(ev_chargers_df['EV Level1 EVSE Num'].sum())
    level_2_count = int(ev_chargers_df['EV Level2 EVSE Num'].sum())
    dc_fast_count = int(ev_chargers_df['EV DC Fast Count'].sum())
    total_chargers = level_1_count + level_2_count + dc_fast_count

    print("\nTotal Number and Type of EV Chargers Installed in Atlanta MSA")
    print("Level 1 EV Chargers:", level_1_count)
    print("Level 2 EV Chargers:", level_2_count)
    print("DC Fast Charging EV Chargers:", dc_fast_count)
    print ("Total EV Chargers Installed: ", total_chargers)

    # Calculate and print the number of EV chargers by access code
    evchargers_access_df = ev_chargers_df.groupby('Access Code')[charger_columns].sum().reset_index()
    print("\nEV Chargers by Access Code:")
    for _, row in evchargers_access_df.iterrows():
        print(f"Access Code: {row['Access Code']}")
        print(f"  Level 1 EV Chargers: {row['EV Level1 EVSE Num']}")
        print(f"  Level 2 EV Chargers: {row['EV Level2 EVSE Num']}")
        print(f"  DC Fast Charging EV Chargers: {row['EV DC Fast Count']}")

    return ev_chargers_df
    # .to_csv("atlanta_msa_ev_chargers.csv", index=False)

print(ev_chargers_data("ev_charging_units_05.19.26.csv"))
