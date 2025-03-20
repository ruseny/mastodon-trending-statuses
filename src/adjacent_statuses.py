"""
This module defines a class to collect data on statuses
that are related to a set of trending statuses as stored 
in a TrendingStatuses object.
"""

# Dependencies
import requests
from datetime import datetime, timezone
from time import sleep
import pandas as pd
from src.mastodon_statuses import MastodonStatuses
from src.trending_statuses import TrendingStatuses

# Class definition
class AdjacentStatuses(MastodonStatuses):
    """
    This class is designed to fetch statuses that are related to a set of 
    trending statuses as stored in a TrendingStatuses object. The related 
    statuses can be those that come immediately after or before the reference
    status in the timeline, and this can be narrowed down to posts coming 
    from the same account. Creating a new instance requires an object of 
    class TrendingStatuses as reference. 
    An authorisation token can be optionally given. If no token is given, 
    the token of the reference object will be used, if it exists. Otherwise,
    requests will be sent without token.
    The method get_data() sends GET requests to Mastodon API to fetch the 
    related statuses. The method generate_df() exports a pandas dataframe
    of the existing data. 
    """
    def __init__(self, reference: TrendingStatuses, token = None) -> None:
        super().__init__(server = reference.server, token = token)
        self.data = {}
        self.reference = reference
        # initialise lists for status and account ids
        # lists with _rem suffix will keep track of statuses for which 
        # data have not yet been fetched
        self.ref_ids = []
        self.ref_ids_rem = []
        self.ref_accounts = []
        self.ref_accounts_rem = []

        # populate the id lists from reference data
        for batch_no in self.reference.data:
            for status in self.reference.data[batch_no]:
                self.ref_ids.append(status["id"])
                self.ref_ids_rem.append(status["id"])
                self.ref_accounts.append(status["account"]["id"])
                self.ref_accounts_rem.append(status["account"]["id"])
        
        # store token if exists
        if token is not None:
            self.token = token
        elif self.reference.token is not None:
            self.token = self.reference.token
        else:
            self.token = None
    
    def get_data(self, mode: str = "subsequent", focus_accounts: str = "no", 
                 status_limit: int = 2, rate_limit_action: str = "wait", 
                 rate_limit_threshold: int = 10, max_wait_seconds: float = 300, 
                 buffer_seconds: float = 10):
        """
        This method sends GET requrests to Mastodon API to fetch the
        related statuses and saves the responses in the data attribute. 
        - The argument 'mode' speficies if the request is for statuses 
        immediately after or before the reference. The value should be
        either 'subsequent' or 'previous'.
        - The argument 'focus_accounts' specifies if the request is for
        statuses that come from the same account that posted the reference
        status. The values should be either 'no' or 'yes'.
        - The argument 'status_limit' specifies how many statuses are
        requested per reference status. The value should be an integer.
        It should be noted that the Mastodon API normally allows a max
        number of 40.
        - The argument 'rate_limit_action' specifies what to do if the
        rate limit is critically low with respect to the defined threshold. 
        The default value is 'wait', which means the method will slow down 
        until the rate limit is reset. Otherwise, the process will abort.
        - The argument 'rate_limit_threshold' specifies the threshold which
        determines when the rate limit is considered critically low. The value
        should be an integer, the default is 10.
        - The argument 'max_wait_seconds' specifies how much to wait, if the
        reset time is not workable. The value should be a float, the default
        is 300.
        - The argument 'buffer_seconds' specifies additional waiting time in
        seconds, to allow a buffer priod for the rate limit to be updated.
        The value should be a float, the default is 10.
        """

        # Firts, check if there are ids for which to fetch data.
        # If no, raise an exception.

        if len(self.ref_ids_rem) == 0:
            raise Exception("No remaining statuses in the reference data")
        elif len(self.ref_accounts_rem) == 0:
            raise Exception("No remaining accounts associated with the reference data")
        
        # Iterate through the list of remaining reference ids while not empty.
        counter = 0
        while len(self.ref_ids_rem) > 0:

            # get remaining status and account ids by removing from the original lists
            s_id = self.ref_ids_rem.pop(0)
            a_id = self.ref_accounts_rem.pop(0)

            # send request based on if we focus on accounts, get response
            if focus_accounts == "yes":
                self.req_account_statuses(account_id = a_id, n_statuses = status_limit, mode = mode, min_max_id = s_id)
            else:
                self.req_timeline(n_statuses = status_limit, mode = mode, min_max_id = s_id)
            
            # if the response is OK, save data and proceed, otherwise skip this item
            if self.response.status_code == 200:
                self.data[s_id] = self.response.json()
                counter += 1
            else:
                print(f"Response code not 200: request failed for status with id {s_id}.\n", 
                      "No data will be saved for this status.")
                continue
            
            # check remaining rate limit: if too low, apply selected procedure
            rem_rate_limit = int(self.response.headers["x-ratelimit-remaining"])
            if rem_rate_limit <= rate_limit_threshold:
                print(f"Remaining rate limit is critically low: {rem_rate_limit}.", 
                      f"\n So far completed {counter} requests.")
                
                if rate_limit_action == "wait":
                    
                    # next reset time as provided in the response headers
                    next_reset = datetime.strptime(
                        self.response.headers['x-ratelimit-reset'], 
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).replace(tzinfo = timezone.utc)
                    print("The provided reset time (UTC):", next_reset.strftime("%H:%M:%S"))

                    time_until = (next_reset - datetime.now(timezone.utc)).total_seconds()

                    # sometimes the info is not updated and the reset time is in the past
                    if time_until <= 0: 
                        print("This has already passed. Current time (UTC):", 
                              datetime.now(timezone.utc).strftime("%H:%M:%S"), 
                              f"\n Instead, waiting {max_wait_seconds + buffer_seconds} seconds...")
                        sleep(max_wait_seconds + buffer_seconds)

                    # otherwise wait until the promised time
                    else:
                        print("Current time (UTC):", 
                              datetime.now(timezone.utc).strftime("%H:%M:%S") +  
                              f". Waiting {round(time_until) + buffer_seconds} seconds... ")
                        sleep(round(time_until) + buffer_seconds)

                    print("Current time (UTC):", 
                          datetime.now(timezone.utc).strftime("%H:%M:%S"),
                          "Resuming the process...")

                #if the choice is not to wait, end the while loop
                else:
                    print("Ending the process.")
                    break
        
        self.response = None

    def generate_df(self, drop_trending: bool = True):
        """
        This method exports the fetched data as a pandas dataframe.
        Ideally, we don't want the related status to be among 
        trending statuses: drop_trending argument is set to True
        by default to drop these.
        """

        # All fetched statuses as a single list of dictionaries
        list_of_dicts = []
        for ref_id in self.data:
            list_of_dicts += self.data[ref_id]
        
        # Use pandas method for converting json to df
        df = pd.json_normalize(list_of_dicts, sep = "_")
        df.drop_duplicates(subset = "id", keep = "last", inplace = True)

        # Check if any of the fetched statuses are also in the reference list
        if drop_trending:
            return df[~df["id"].isin(self.ref_ids)]
        else:
            return df
        