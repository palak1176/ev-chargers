import pandas as pd

def ev_chargers_data(file_path):
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

    columns_to_keep = ['City', 'EV Level1 EVSE Num', 'EV Level2 EVSE Num', 'EV DC Fast Count'] # could be nice to have these columns if needed: 'Date Last Confirmed', 'Updated At', 'Access Code', 'Access Detail Code'
    ev_chargers_df = ev_chargers_df[columns_to_keep]

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

    ev_chargers_df['City'] = ev_chargers_df['City'].str.strip().str.title()
    ev_chargers_df = ev_chargers_df[ev_chargers_df['City'].isin(atlanta_msa_cities)]

    #print(ev_chargers_df)
    charger_columns = ['EV Level1 EVSE Num', 'EV Level2 EVSE Num', 'EV DC Fast Count']
    ev_chargers_df[charger_columns] = ev_chargers_df[charger_columns].fillna(0).astype(int)
    
    level_1_count = int(ev_chargers_df['EV Level1 EVSE Num'].sum())
    level_2_count = int(ev_chargers_df['EV Level2 EVSE Num'].sum())
    dc_fast_count = int(ev_chargers_df['EV DC Fast Count'].sum())
    total_chargers = level_1_count + level_2_count + dc_fast_count

    print("\nNumber and Type of EV Chargers Installed in Atlanta MSA")
    print("Level 1 EV Chargers:", level_1_count)
    print("Level 2 EV Chargers:", level_2_count)
    print("DC Fast Charging EV Chargers:", dc_fast_count)
    return f"Total EV Chargers Installed: {total_chargers}\n"

print(ev_chargers_data("ev_charging_units_05.19.26.csv"))
