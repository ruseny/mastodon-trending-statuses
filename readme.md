# Predicting trending posts on mastodon.social

This project is developed to:
- Fetch data from mastodon.social about trending posts (statuses)
- Process and clean these data into datasets that can be used for analyses and machine/deep learning
- Build model(s) to predict which statuses are likely to be trending

## Fetching and processing data

Custom modules are used to interact with Mastodon API to fetch data. This was done instead of feature-complete solutions, such as Mastodon.py ([documentation](https://mastodonpy.readthedocs.io/en/stable/), [repo](https://github.com/halcy/Mastodon.py)), because modules needed to be tailor-made to specific purposes:
- The trending statuses over a period of time needed to be accumulated
- For each trending status, a few non-trending statuses were needed for classification

These modules are under directory 'src':
- app_setup.py: can register an app with Mastodon API, get an authentication token and save it to a file
- trending_statuses.py: can request trending statuses from a Mastodon server, keep requesting until all such posts are fetched, and export these in the form of a dataframe
- adjacent_statuses.py: for each trending status, can request a number of adjacent statuses (close in time, either immediately before or immediately after), taking breaks when rate limits are reached, and export these in the form of a dataframe
- data_cleaning.py: a number of functions to perform data cleaning tasks, specialised for the dataframe structure of Mastodon statuses

The following files under directory 'scripts' perform the data collection:
- get_app_token.py: for initial app creation, ideally run only once
- collect_data.py: to fetch trending statuses at the time of running the script, as well as their adjacent statuses, and to save these as both raw (class instances as pkl files) and processed (pandas dataframes) data files
- clean_data.py: to get all files under directory 'data/processed' (created by the above script), conduct cleaning operations, and save as pandas dataframes
- crontab.txt: sample cron job for a linux operating system, only applicable in the original local environment, to run the script over a weekend from Saturday to Monday four times a day, and save the terminal output in a log file

## Building a model

The model building is documented in jupyter notebooks in directory 'notebooks'. The strategy is to fine-tune DistilBERT for a classification model.
- text_data_prep.ipynb: takes cleaned dataframes, as produced by above scripts, and saves datasets of only text and label
- nlp_model.ipynb: uses Hugging Face Transformers to get DistilBERT, adjust the text dataset, fit the classification model, and save it 

## Requirements and replication

The file environment.yml specifies the dependencies of the (conda) virtual environment of the project. `conda env create -f environment.ym` can be used to create the same environment.