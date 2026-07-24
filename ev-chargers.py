import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

def filter_by_boundary(ev_chargers_df, boundary_path, predicate="within"):
    """
    Spatial-join approach: keep only stations whose Longitude/Latitude
    point falls inside the given ArcGIS boundary layer.

    boundary_path can be:
      - a local shapefile/geojson path, or
      - an ArcGIS Feature Service query URL
    """
    # Drop rows without coordinates before building geometries
    coordinates_present = ev_chargers_df['Longitude'].notna() & ev_chargers_df['Latitude'].notna()
    missing_coordinatess = (~coordinates_present).sum()
    if missing_coordinatess:
        print(f"Warning: {missing_coordinatess} rows are missing Longitude/Latitude and will be dropped from the boundary join.")
    ev_chargers_df = ev_chargers_df[coordinates_present].copy()

    geometry = [Point(xy) for xy in zip(ev_chargers_df['Longitude'], ev_chargers_df['Latitude'])]
    stations_gdf = gpd.GeoDataFrame(ev_chargers_df, geometry=geometry, crs="EPSG:4326")

    boundary_gdf = gpd.read_file(boundary_path)
    if boundary_gdf.crs is None:
        raise ValueError("Boundary layer has no CRS defined — check the source file.")
    boundary_gdf = boundary_gdf.to_crs("EPSG:4326")

    # Dissolve in case the boundary layer has multiple polygon features (e.g. one per county)
    boundary_union = boundary_gdf.dissolve().reset_index(drop=True)

    joined = gpd.sjoin(stations_gdf, boundary_union, how="inner", predicate=predicate)

    # Drop the join's extra index/attribute columns from the boundary layer, keep original columns + geometry
    keep_cols = [c for c in ev_chargers_df.columns] + ['geometry']
    return pd.DataFrame(joined[keep_cols])


def ev_chargers_data(file_path, boundary_path, predicate="within"):
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
    
    # Check for required columns
    must_have_columns = ['ID', 'City', 'EV Level1 EVSE Num', 'EV Level2 EVSE Num', 'EV DC Fast Count', 'Access Code', 'EV Network', 
                       'EV J1772 Connector Count', 'EV CCS Connector Count', 'EV CHAdeMO Connector Count', 'EV J3400 Connector Count', 
                       'EV J3271 Connector Count', 'Open Date', 'Date Last Confirmed'] 
    missing_cols = [col for col in must_have_columns if col not in ev_chargers_df.columns] 
    if missing_cols:
        print(f"Missing columns: {missing_cols}")
        return None

    # Filter to stations within the boundary
    ev_chargers_df = filter_by_boundary(ev_chargers_df, boundary_path, predicate=predicate)
    
    # Clean 'Access Code' column and fill missing values with 'Unknown'
    ev_chargers_df['Access Code'] = ev_chargers_df['Access Code'].fillna('Unknown').str.strip().str.title().astype(str)
    
    # Fill missing values in charger/connector count columns with 0 and convert to integers
    charger_columns = ['EV Level1 EVSE Num', 'EV Level2 EVSE Num', 'EV DC Fast Count']
    connector_columns = ['EV J1772 Connector Count', 'EV CCS Connector Count', 'EV CHAdeMO Connector Count',
                        'EV J3400 Connector Count', 'EV J3271 Connector Count']
    ev_chargers_df[charger_columns] = ev_chargers_df[charger_columns].fillna(0).astype(int)
    ev_chargers_df[connector_columns] = ev_chargers_df[connector_columns].fillna(0).astype(int)
    
    # Aggregate data by station ID to get unique stations and their total chargers/connectors
    station_df = (ev_chargers_df.groupby('ID', as_index=False).agg({
        # Metadata
        'City': 'first',
        'Station Name': 'first',
        'Street Address': 'first',
        'Longitude': 'first',
        'Latitude': 'first',
        'Status Code': 'first',
        'Access Code': 'first',
        'Groups With Access Code': 'first',
        'Access Days Time': 'first',
        'EV Network': 'first',
        'Open Date': 'first',
        'Date Last Confirmed': 'first',
        'EV Connector Types': 'first',

        # EVSE counts (identical for every row of a station)
        'EV Level1 EVSE Num': 'max',
        'EV Level2 EVSE Num': 'max',
        'EV DC Fast Count': 'max',

        # Connector counts
        'EV J1772 Connector Count': 'sum',
        'EV CCS Connector Count': 'sum',
        'EV CHAdeMO Connector Count': 'sum',
        'EV J3400 Connector Count': 'sum',
        'EV J3271 Connector Count': 'sum',}))

    # Count temporarily unavailable stations (Status Code 'T') and exclude them from the main station_df
    unavailable_df = station_df[station_df['Status Code'] == 'T']
    print("\nTemporarily Unavailable EV Chargers (excluded from all totals below):")
    print(unavailable_df[charger_columns].sum())
    station_df = station_df[station_df['Status Code'] != 'T']
    
    # Calculate total chargers by type and overall total
    level_1_count = int(station_df['EV Level1 EVSE Num'].sum())
    level_2_count = int(station_df['EV Level2 EVSE Num'].sum())
    dc_fast_count = int(station_df['EV DC Fast Count'].sum())
    total_chargers = level_1_count + level_2_count + dc_fast_count

    print(f"\nTotal Number and Type of EV Chargers Installed")
    print(f"Level 1 EV Chargers: {level_1_count}")
    print(f"Level 2 EV Chargers: {level_2_count}")
    print(f"DC Fast Charging EV Chargers: {dc_fast_count}")
    print(f"Total EV Chargers Installed: {total_chargers}")

    # Calculate and print the number of EV chargers by access code
    ev_chargers_access_df = station_df.groupby('Access Code')[charger_columns].sum().reset_index()
    print("\nEV Chargers by Access Code:")
    for _, row in ev_chargers_access_df.iterrows():
        print(f"Access Code: {row['Access Code']}")
        print(f"  Level 1 EV Chargers: {row['EV Level1 EVSE Num']}")
        print(f"  Level 2 EV Chargers: {row['EV Level2 EVSE Num']}")
        print(f"  DC Fast Charging EV Chargers: {row['EV DC Fast Count']}")

    # Calculate and print the number of connectors by type
    ev_chargers_connectors_df = station_df[connector_columns].sum().reset_index()
    print("\nTotal Number of Connectors by Type:")
    for _, row in ev_chargers_connectors_df.iterrows():
        print(f"{row['index']}: {row[0]}")
    total_connectors = station_df[connector_columns].sum().sum()
    print(f"Total Connectors Installed: {total_connectors}")

    # Count stations with missing connector counts (where EVSE count > 0 but connector count = 0)
    station_df['EVSE Total'] = station_df[charger_columns].sum(axis=1)
    station_df['Connector Total'] = station_df[connector_columns].sum(axis=1)
    missing = station_df[(station_df['Connector Total'] == 0) & (station_df['EVSE Total'] > 0)]
    print("\nEach station should have at least one connector for each EVSE, so the minimum number of connectors not captured is:", missing['EVSE Total'].sum())

    print("\nCumulative EV Chargers Installed Over Time")
    # Ensure 'Open Date' is in datetime format and handle errors
    station_df['Open Date'] = pd.to_datetime(station_df['Open Date'], errors='coerce')

    if station_df['Open Date'].isnull().any():
        # Use 'Date Last Confirmed' as a fallback for missing 'Open Date' values
        station_df['Date Last Confirmed'] = pd.to_datetime(station_df['Date Last Confirmed'], errors='coerce')
        station_df['Open Date'] = station_df['Open Date'].fillna(station_df['Date Last Confirmed'])

    # Extract year from 'Open Date'
    station_df['Year'] = station_df['Open Date'].dt.year   

    # Years to evaluate
    target_years = [2005, 2010, 2015, 2020, 2025, 2026]

    # Build cumulative counts for each type of charger and overall total
    cumulative_counts = []
    for year in target_years:
        level_1_cumulative = station_df[station_df['Year'] <= year]['EV Level1 EVSE Num'].sum()
        level_2_cumulative = station_df[station_df['Year'] <= year]['EV Level2 EVSE Num'].sum()
        dc_fast_cumulative = station_df[station_df['Year'] <= year]['EV DC Fast Count'].sum()
        total_cumulative = level_1_cumulative + level_2_cumulative + dc_fast_cumulative
        cumulative_counts.append({
            'Year': year,
            'Level 1 Cumulative': level_1_cumulative,
            'Level 2 Cumulative': level_2_cumulative,
            'DC Fast Cumulative': dc_fast_cumulative,
            'Total Cumulative': total_cumulative
        })

    # Convert to DataFrame
    ev_chargers_cumulative_df = pd.DataFrame(cumulative_counts)
    # Print cumulative counts
    print(ev_chargers_cumulative_df.to_string(index=False))
    print("Note: Cumulative counts are based on the 'Open Date' of each station. If 'Open Date' is missing, 'Date Last Confirmed' is used as a fallback.\n")

    return station_df
    # .to_csv("atlanta_msa_ev_chargers.csv", index=False)


if __name__ == "__main__":
    mpo_boundary_url = (
        "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/"
        "Atlanta_Region_Planning_Areas/FeatureServer/0/query"
        "?where=REGION%20IN%20('MPA%202024')"
        "&outFields=*"
        "&f=geojson")
    msa_boundary_url = (
        "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/"
        "Atlanta_Region_Planning_Areas/FeatureServer/0/query"
        "?where=REGION%20IN%20('MSA_CBSA%202010')"
        "&outFields=*"
        "&f=geojson")

    result = ev_chargers_data(
        "alt_fuel_stations_ev_charging_units (Jul 18 2026).csv",
        boundary_path=msa_boundary_url,)
    print(result)
