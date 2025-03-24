#!/bin/bash

dir_scripts="/home/rusen/github-repos/mastodon-trending-statuses/testing/scripts/"
dir_logs="/home/rusen/github-repos/mastodon-trending-statuses/testing/logs/"

if [[ ! -e $dir_logs ]]; then
    mkdir -p $dir_logs
fi

log_delim="### NEW RUN on $(date) ###"

echo $log_delim >> ${dir_logs}collect_data.log
echo $log_delim >> ${dir_logs}clean_data.log

cd $dir_scripts
conda run -n mastodon python test_collect_data.py \
    >> ${dir_logs}collect_data.log 2>&1 \
    && conda run -n mastodon python test_clean_data.py \
    >> ${dir_logs}clean_data.log 2>&1