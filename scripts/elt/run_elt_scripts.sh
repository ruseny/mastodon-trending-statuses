#!/bin/bash

dir_scripts="/home/rusen/github-repos/mastodon-trending-statuses/scripts/"
dir_logs="/home/rusen/github-repos/mastodon-trending-statuses/logs/"

if [[ ! -e $dir_logs ]]; then
    mkdir -p $dir_logs
fi

cd $dir_scripts
conda run -n mastodon python collect_data.py \
    >> ${dir_logs}collect_data.log 2>&1 \
    && conda run -n mastodon python clean_data.py \
    >> ${dir_logs}clean_data.log 2>&1