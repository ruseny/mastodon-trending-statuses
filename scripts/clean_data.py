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
    # get the list of files in the directory
    list_files = [f for f in os.listdir("../data/processed") if os.path.isfile(os.path.join("../data/processed", f))]

    # prepare paths for trending and adjacent
    paths_trending = [os.path.join("../data/processed", f) for f in list_files if f[:8] == "trending"]
    paths_adjacent = [os.path.join("../data/processed", f) for f in list_files if f[:8] == "adjacent"]
    paths_trending.sort()
    paths_adjacent.sort()

    # output df names will have the timestamp of the corresponding trending statuses
    df_names = ["df" + f[17:33] for f in list_files if f[:8] == "trending"]

    # match trending datasets with correponding adjacent datasets
    match_dfs = {}
    for path in paths_trending:
        i = paths_trending.index(path)
        match_dfs[path] = paths_adjacent[i*4 : (i+1)*4]
    
    # collect processed dfs in a dictionary
    dict_dfs = {}
    for path, name in zip(match_dfs.keys(), df_names):
        # first the trending :
        main_df = pd.read_csv(path, index_col = 0)
        # process:
        main_df = clean_data(main_df)
        main_df = keep_only_english(main_df)
        main_df = reduce_df(main_df)
        main_df["trend"] = "trending"
        # next, go through the adjacent:
        for adj_path in match_dfs[path]:
            trend_type = "adjacent_" + str(match_dfs[path].index(adj_path) + 1)
            adj_df = pd.read_csv(adj_path, index_col = 0)
            # process:
            adj_df = clean_data(adj_df)
            adj_df = keep_only_english(adj_df)
            adj_df = reduce_df(adj_df)
            adj_df["trend"] = trend_type
            # add to the trending
            main_df = pd.concat([main_df, adj_df])
        # store in the dict
        dict_dfs[name] = main_df.reset_index(drop = True)

    # save
    for df_name in dict_dfs:
        df = dict_dfs[df_name]
        path = "../data/cleaned/" + df_name + ".pkl"
        df.to_pickle(path)

if __name__ == "__main__":
    main()