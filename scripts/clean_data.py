"""
This script gets all files from the directory ../data/processed
and returns cleaned datasets into the directory ../data/cleaned
"""

import os
import pandas as pd

import sys
sys.path.append("../")
from src.data_cleaning import clean_data, keep_only_english, reduce_df

import warnings
from bs4 import MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module='src.data_cleaning')

def main():

    print("Checking for datasets to transform...")

    # get the list of files in the processed directory
    list_files = [f for f in os.listdir("../data/processed") if os.path.isfile(os.path.join("../data/processed", f))]

    # check the processed directory, stop if empty
    if len(list_files) == 0:
        print("The directory ../data/processed is empty. Please run the script get_data.py first.")
        return
    else:
        print(f"Found {len(list_files)} files in the directory ../data/processed.")
    
    # check if the cleaned directory exists, if so, get the list of files in it
    if os.path.exists("../data/cleaned"):
        list_files_cleaned = [f for f in os.listdir("../data/cleaned") if os.path.isfile(os.path.join("../data/cleaned", f))]
        # if it is not empty, remove the existing file names from the list of files to be cleaned, based on timestamps
        if len(list_files_cleaned) > 0:
            print(f"Found {len(list_files_cleaned)} files in the directory ../data/cleaned.")
            already_cleaned_timestamps = [name[-19:-4] for name in list_files_cleaned]
            list_files = [f for f in list_files if f[-19:-4] not in already_cleaned_timestamps]
            # if there is no more files to clean, stop
            if len(list_files) == 0:
                print("All files in the directory ../data/processed had been transformed already.")
                return
            else:
                print(f"Cleaning {len(list_files)} files.")
        else:
            print("The directory ../data/cleaned is empty. All files in the directory ../data/processed will be transformed.")
    # if the cleaned directory does not exist, create it
    else:
        print("Creating directory ../data/cleaned.")
        os.mkdir("../data/cleaned")

    # prepare paths for trending and adjacent
    paths_trending = [os.path.join("../data/processed", f) for f in list_files if f[:8] == "trending"]
    paths_adjacent = [os.path.join("../data/processed", f) for f in list_files if f[:8] == "adjacent"]
    paths_trending.sort()
    paths_adjacent.sort()

    # output df names will have the timestamp of the corresponding trending statuses
    df_names = ["df_" + f[-19:-4] for f in list_files if f[:8] == "trending"]

    # match trending datasets with correponding adjacent datasets, based on timestamps
    match_dfs = {}
    for path in paths_trending:
        match_dfs[path] = [p for p in paths_adjacent if path[-19:-4] in p]
    
    # collect processed dfs in a dictionary
    dict_dfs = {}
    for path, name in zip(match_dfs.keys(), df_names):
        # first the trending :
        print(f"Reading df: {path}...")
        main_df = pd.read_csv(path, index_col = 0)
        # process:
        print("...processing...")
        main_df = clean_data(main_df)
        main_df = keep_only_english(main_df)
        main_df = reduce_df(main_df)
        main_df["trend"] = "trending"
        # next, go through the adjacent:
        for adj_path in match_dfs[path]:
            trend_type = "adjacent_" + str(match_dfs[path].index(adj_path) + 1)
            print(f"Reading df: {adj_path}...")
            adj_df = pd.read_csv(adj_path, index_col = 0)
            # process:
            print("...processing...")
            adj_df = clean_data(adj_df)
            adj_df = keep_only_english(adj_df)
            adj_df = reduce_df(adj_df)
            adj_df["trend"] = trend_type
            # add to the trending
            print("...merging...")
            main_df = pd.concat([main_df, adj_df])
        # store in the dict
        print("dfs merged.")
        dict_dfs[name] = main_df.reset_index(drop = True)

    # save
    for df_name in dict_dfs:
        df = dict_dfs[df_name]
        path = "../data/cleaned/" + df_name + ".pkl"
        print(f"Saving transformed df to: {path}")
        df.to_pickle(path)

if __name__ == "__main__":
    main()