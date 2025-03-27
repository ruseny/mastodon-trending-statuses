#!/bin/bash

# This bash script runs two python scripts in their own conda environment
# and from their own directory. It also logs the output of the scripts.

# Define the directories for the scripts and log files
dir_scripts="/home/rusen/github-repos/mastodon-trending-statuses/scripts/"
dir_logs="/home/rusen/github-repos/mastodon-trending-statuses/logs/"

# Create the logs directory if it doesn't exist
if [[ ! -e $dir_logs ]]; then
    mkdir -p $dir_logs
fi

# A delimiter line for the log files
log_delim="### NEW RUN on $(date) ###"
# Write the delimiter line to the log files
echo $log_delim >> ${dir_logs}collect_data.log
echo $log_delim >> ${dir_logs}clean_data.log

# Change to the directory of the scripts
cd $dir_scripts
# Run the two python scripts in sequence, logging the output
conda run -n mastodon python collect_data.py \
    >> ${dir_logs}collect_data.log 2>&1 \
    && conda run -n mastodon python clean_data.py \
    >> ${dir_logs}clean_data.log 2>&1