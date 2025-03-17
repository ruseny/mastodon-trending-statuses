"""
This script fetches data on trending statuses and their adjacent statuses, 
and saves them to pickle files containing corresponding class objects.
"""

import os
import sys
import pickle
from datetime import datetime
import pandas as pd

sys.path.append("../")
from src.trending_statuses import TrendingStatuses
from src.adjacent_statuses import AdjacentStatuses

def prep_dirs():
    # Create necessary directories, if don't not exist
    if not os.path.exists("../data/raw"):
        print("Creating directory '../data/raw'")
        os.mkdir("../data/raw")
    if not os.path.exists("../data/processed"):
        print("Creating directory '../data/processed'")
        os.mkdir("../data/processed")
    if not os.path.exists("../data/cleaned"):
        print("Creating directory '../data/cleaned'")
        os.mkdir("../data/cleaned")

def check_app_token():
    # If an authorisation token is stored, as defined in
    # the script get_app_token, use it. Otherwise, proceed
    # without token.
    print("Looking for authorisation token in '../credentials/app_token.txt'")
    if os.path.exists("../credentials/app_token.txt"):
        print("Token found")
        with open("../credentials/app_token.txt") as t:
            return t.read()
    else:
        print("Authorisation token not found.", 
              "\nA new token can be created by running the script get_app_token.py.", 
              "\nProceeding without token.")
        return None

def get_trending(app_token = None):
    
    # Get trending status data as class instance
    trending_statuses = TrendingStatuses(token = app_token)

    # Get data
    print("WORKING ON TRENDING STATUS DATA...")
    trending_statuses.get_data()
    # Narrow down to English language posts
    trending_statuses.reduce_single_lang(overwrite = True)
    print("...DATA FETCHED.")

    return trending_statuses

def get_adjacent(reference, mode, focus_accounts):

    # Get adjacent status data as class instance
    adjacent_statuses = AdjacentStatuses(reference=reference)

    # Get data
    print(f"WORKING ON ADJACENT STATUS DATA (mode: {mode}, account focus: {focus_accounts})...")
    adjacent_statuses.get_data(mode = mode, focus_accounts = focus_accounts)
    print("...DATA FETCHED.")

    return adjacent_statuses

def save_raw_and_processed(data, type, time_stamp):
    # Save class instances as raw data, and pandas dataframes as processed data

    # Define file paths and names
    file_path_r = f"../data/raw/{type}_{time_stamp}.pkl"
    file_path_p = f"../data/processed/{type}_{time_stamp}.csv"

    # Save raw data
    print("SAVING RAW DATA...")
    with open(file_path_r, "wb") as output:
        pickle.dump(data, output)
    print(f"...RAW DATA SAVED TO FILE: {file_path_r}...")

    # Save processed data
    print("...EXPORTING DATAFRAME AND SAVING...")
    df = data.generate_df()
    df.to_csv(file_path_p)
    print(f"...DATAFRAME SAVED TO FILE: {file_path_p}.")

if __name__ == "__main__":
    
    # prep
    prep_dirs()
    app_token = check_app_token()

    # trending
    time_stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    trending_statuses = get_trending(app_token = app_token)
    save_raw_and_processed(trending_statuses, "trending_statuses", time_stamp)

    # adjacent, run for each mode and focus, name accordingly
    for mode in ["previous", "subsequent"]:
        for focus in ["no", "yes"]:
            type_name = f"adjacent_statuses_{mode}_acc_focus_{focus}"
            adjacent_statuses = get_adjacent(reference = trending_statuses, mode = mode, focus_accounts = focus)
            save_raw_and_processed(adjacent_statuses, type_name, time_stamp)

