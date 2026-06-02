import pandas as pd

atlanta_msa_cities = [
"Acworth", "Adairsville", "Aldora", "Alpharetta", "Atlanta", "Auburn", "Austell", "Avondale Estates", 
"Ball Ground", "Barnesville", "Berkeley Lake", "Bethlehem", "Between", "Bostwick", "Bowdon", "Braselton", 
"Braswell", "Bremen", "Brookhaven", "Brooks", "Buchanan", "Buckhead", "Buford", "Canton", "Carl", "Carrollton", 
"Cartersville", "Centralhatchee", "Chamblee", "Chattahoochee Hills", "Clarkston", "College Park", "Concord", 
"Conyers", "Covington", "Cumming", "Dacula", "Dallas", "Dawsonville", "Decatur", "Doraville", "Douglasville", 
"Duluth", "Dunwoody", "East Point", "Emerson", "Ephesus", "Euharlee", "Fairburn", "Fayetteville", "Flovilla", 
"Forest Park", "Franklin", "Gay", "Good Hope", "Grantville", "Grayson", "Greenville", "Griffin", "Hampton", 
"Hapeville", "Harrison", "Hiram", "Holly Springs", "Jackson", "Jasper", "Jenkinsburg", "Jersey", "Johns Creek", 
"Jonesboro", "Kennesaw", "Kingston", "Lake City", "Lawrenceville", "Mableton", "Lilburn", "Lithonia", "Locust Grove", 
"Loganville", "Lone Oak", "Lovejoy", "Luthersville", "Madison", "Manchester", "Mansfield", "Marietta", "McDonough", 
"Meansville", "Milner", "Milton", "Molena", "Monroe", "Monticello", "Moreland", "Morrow", "Mount Zion", "Mountain Park", 
"Mulberry", "Nelson", "Newborn", "Newnan", "Norcross", "Orchard Hill", "Oxford", "Peachtree City", "Peachtree Corners", 
"Pine Lake", "Porterdale", "Powder Springs", "Rest Haven", "Riverdale", "Roberta", "Rockmart", "Roswell", "Rutledge", 
"Sandy Springs", "Senoia", "Shady Dale", "Sharpsburg", "Smyrna", "Snellville", "Social Circle", "South Fulton", "Statham", 
"Stockbridge", "Stone Mountain", "Stonecrest", "Sugar Hill", "Sunny Side", "Suwanee", "Talking Rock", "Tallapoosa", 
"Taylorsville", "Temple", "Tucker", "Turin", "Tyrone", "Union City", "Villa Rica", "Waco", "Waleska", "Walnut Grove", 
"Warm Springs", "White", "Whitesburg", "Williamson", "Winder", "Woodbury", "Woodstock", "Woolsey", "Zebulon"]

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
    columns_to_keep = ['City', 'EV Level1 EVSE Num', 'EV Level2 EVSE Num', 'EV DC Fast Count', 'Access Code', 'EV Network', 
                       'EV J1772 Connector Count', 'EV CCS Connector Count', 'EV CHAdeMO Connector Count', 'EV J3400 Connector Count', 'EV J3271 Connector Count'] 
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
    ev_chargers_access_df = ev_chargers_df.groupby('Access Code')[charger_columns].sum().reset_index()
    print("\nEV Chargers by Access Code:")
    for _, row in ev_chargers_access_df.iterrows():
        print(f"Access Code: {row['Access Code']}")
        print(f"  Level 1 EV Chargers: {row['EV Level1 EVSE Num']}")
        print(f"  Level 2 EV Chargers: {row['EV Level2 EVSE Num']}")
        print(f"  DC Fast Charging EV Chargers: {row['EV DC Fast Count']}")

    # Calculate and print the number of connectors by type 
    connector_columns = ['EV J1772 Connector Count', 'EV CCS Connector Count', 'EV CHAdeMO Connector Count', 'EV J3400 Connector Count', 'EV J3271 Connector Count']
    ev_chargers_connectors_df = ev_chargers_df[connector_columns].sum().reset_index()
    print("\nTotal Number of Connectors by Type:")
    for _, row in ev_chargers_connectors_df.iterrows():
        print(f"{row['index']}: {row[0]}")

    # Calculate and print the charging ports by charging network for each type of charger
    ev_chargers_network_df = ev_chargers_df.groupby('EV Network')[charger_columns].sum().reset_index()
    print("\nEV Chargers by Charging Network:")
    for _, row in ev_chargers_network_df.iterrows():
        print(f"Charging Network: {row['EV Network']}")
        print(f"  Level 1 EV Chargers: {row['EV Level1 EVSE Num']}")
        print(f"  Level 2 EV Chargers: {row['EV Level2 EVSE Num']}")
        print(f"  DC Fast Charging EV Chargers: {row['EV DC Fast Count']}")

    # return ev_chargers_df
    # .to_csv("atlanta_msa_ev_chargers.csv", index=False)

print(ev_chargers_data("alt_fuel_stations_ev_charging_units (Jun 2 2026).csv"))
