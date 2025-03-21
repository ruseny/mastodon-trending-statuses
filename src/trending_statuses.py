"""
This module defines a class to collect data on trending statuses.
"""

# Dependencies
import requests
from datetime import datetime, timedelta
import pandas as pd
from src.mastodon_statuses import MastodonStatuses

# A class with methods to get data
class TrendingStatuses(MastodonStatuses):
    """
    This class can get and store data from trending mastodon statuses.
    - The argument 'server' specifies the Mastodon instance to send the
    requests. This should be a string that will resolve into a valid URL.
    If this is not specified, it defaults to 'mastodon.social'.
    - With the argument 'token', one can optionally pass an authorisation
    token. This is normally not required to fetch trending statuses.
    The class is initialised with the main attribute 'data', which stores
    the trending status data as provided by mastodon API when the method
    get_data() is called. This is a dictionary where the keys are batch 
    numbers, and the values are list of statuses fetched in this batch.
    There is also a data_single_lang attribute, which stores the data in
    the same way, if the method reduce_single_lang() is called without
    overwriting the main data.
    After fetching data, these can be turned into a pandas dataframe with 
    the method generate_df(). 
    The class also inherits some basic properties and methods from the 
    MastodonStatuses class.
    """
    def __init__(self, server: str = None, token : str = None) -> None:
        super().__init__(server = server, token = token)
        
        self.data = {}
        self.data_single_lang = None
        
    def get_data(self, verbose: bool = True, max_batches: int = 25, n_per_batch: int = 40,
                 last_n_hours: float = 48, offset: int = 0) -> None:
        """
        This method sends requests to mastodon.social API to fetch trending statuses.
        Since there is a limit on the maximum number of statuses per request, data are
        fetched in batches, using the API's pagination.
        Args:
        - max_batches (int): the maximum number of batches that will be fetched, i.e.
        the maximum number of requests that will be sent. The default is 25.
        - last_n_hours (float): the number of hours prior to the curent datetime, 
        which will stop the request if an earlier status is fetched. Statuses don't
        arrive in reverse chronological order, so this doesn't necessarily get all 
        statuses within this interval. The default value is 48, which usually covers
        all the statuses that the API provides. Lower values can be used to shorten
        the process.
        - n_per_batch (int): the maximum number of statuses that will be fetched per request.
        The default value is 40, which is usually the maximum that the API allows; 
        values above 40 may not work, and create unnecessarily high incrementation of the offset, 
        leading to failure to fetch all statuses.
        - offset (int): the starting value of the offset, which can be used to skip a certain 
        number of statuses. The default value is 0.
        Returns: the statuses are appended to the data attribute of the class. These may include
        duplicates, especially if the method is called in short time intervals.
        """
        time_reached = datetime.now()
        statuses_after = time_reached - timedelta(hours = last_n_hours)
        batch_n = len(self.data) + 1 # if the class instance already has data, this is not overwritten
        req_counter = 0 # to control for max batches

        # check if the max number of batches has been reached and
        # if any status earlier than the specified timeframe has been fetched
        # time reached is updated within the loop
        while (req_counter < max_batches) and (time_reached > statuses_after):
            # parameter for offset to pass to the URL. The offset is updated in the loop.

            self.req_trending(n_statuses = n_per_batch, offset = offset)

            if self.response.status_code == 200:
                batch_data = self.response.json()
                
                # check if the requested number of statuses is in the batch
                if len(batch_data) == n_per_batch:
                    # append the statuses to the data attribute of the class
                    self.data[batch_n] = batch_data
                    if verbose:
                        print(f"Batch {batch_n} fetched with {len(batch_data)} statuses.")

                    # increment values for the next iteration
                    batch_n += 1
                    offset += n_per_batch
                    req_counter += 1

                    # find the earliest datetime of statuses and update time_reached
                    dts = []
                    for i in range(n_per_batch):
                        dts.append(datetime.strptime(batch_data[i]["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"))
                    time_reached = min(dts)
                
                # if the number of statuses is lower than requested, no more statuses will be provided after this one: end loop
                else:
                    self.data[batch_n] = batch_data
                    if verbose:
                        print(f"Batch {batch_n} fetched with {len(batch_data)} statuses.\n", 
                              f"Last batch has fewer than requested {n_per_batch} statuses. Ending loop.")
                    break 
            
            else:
                print("Response status not 200. Request failed.")
                break
            
            # if explanation needs to be printed, check loop conditions here, and break if necessary
            if verbose and (req_counter >= max_batches):
                print(f"Maximum number of batches {(max_batches)} reached. Stopping requests")
                break
            if verbose and (time_reached <= statuses_after):
                print(f"Statuses fetched are older than {last_n_hours} hours. Stopping requests.")
                break
        
        self.response = None
        self.last_req_type = None
    
    def reduce_single_lang(self, language: str = "en", overwrite: bool = False) -> None:
        """
        This method takes the statuses data collected by
        the get_data method, filters for a single language, 
        and stores the resulting data in the attribute
        data_single_lang. The default language is English.
        Optionally, the original data can be overwritten with
        the single language data.
        """
        data_lang = {}
        for batch_no in self.data:
            data_lang[batch_no] = []
            for status in self.data[batch_no]:
                if status["language"] == language:
                    data_lang[batch_no].append(status)
        if overwrite:
            self.data = data_lang
        else:
            self.data_single_lang = data_lang
    
    def generate_df(self, single_language: bool = False) -> pd.DataFrame:
        """
        This method takes the statuses data collected by
        the get_data method and returns a pandas dataframe. 
        The json structure is flattened and duplicates are removed.
        It can be specified if the single language data is used; 
        if this doesn't exist, the main data will be used.
        """
        list_of_dicts = []

        if single_language and self.data_single_lang:
            for batch_no in self.data_single_lang:
                list_of_dicts += self.data_single_lang[batch_no]
        else:
            for batch_no in self.data:
                list_of_dicts += self.data[batch_no]
        
        df = pd.json_normalize(list_of_dicts, sep = "_")
        return df.drop_duplicates(subset = "id", keep = "last")
