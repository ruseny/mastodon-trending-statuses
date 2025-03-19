"""
This module defines a class to send a request to the Mastodon API,
and store the response. It is designed to be the parent class of 
other classes that will send specific types of requests, in order 
to simplify the definitions of these children classes.
"""

# dependency
import requests

# class definition
class MastodonStatuses:
    """
    This class sends a request to the Mastodon API, and stores the response.
    - The argument 'server' specifies the Mastodon instance to send the
    requests. This should be a string that will resolve into a valid URL.
    If no server is specified, it defaults to 'mastodon.social'.
    - The argument 'token' is an authorisation token. This is optional, and
    is normally not required to fetch trending statuses, but can be useful
    for consistency.
    The methods of the class can send three types of requests:
    - req_trending() fetches trending statuses.
    - req_timeline() fetches statuses from the public timeline.
    - req_account_statuses() fetches statuses from a specific account.
    The response from the API is stored in the attribute 'response', and
    the type of the last request is stored in 'last_req_type'.
    """

    def __init__(self, server : str = None, token : str = None) -> None:
        if server:
            self.server = server
        else:
            self.server = "mastodon.social"
        self.server_url = f"https://{self.server}/"
        self.token = token
        if self.token:
            self.headers = {"Authorization": f"Bearer {self.token}"}
        self.response = None
        self.last_req_type = None

    def req_trending(self, n_statuses : int = 40, offset : int = 0) -> None:
        """
        This method sends a request to the Mastodon API to fetch trending statuses.
        - The argument 'n_statuses' specifies the number of statuses to fetch,
        and is used as the 'limit' parameter in the request.
        - The argument 'offset' specifies the number of statuses to skip,
        and is used as the 'offset' parameter in the request.
        """

        req_url = f"{self.server_url}api/v1/trends/statuses?limit={n_statuses}&offset={offset}"

        if self.token:
            self.response = requests.get(req_url, headers=self.headers)
        else:
            self.response = requests.get(req_url)
        
        self.last_req_type = "trending"
    
    def req_timeline(self, n_statuses : int = 40, 
                     mode : str = None, min_max_id : str = None) -> None:
        """
        This method sends a request to the Mastodon API to fetch statuses from 
        the public timeline. 
        - The argument 'n_statuses' specifies the number of statuses to fetch,
        and is used as the 'limit' parameter in the request.
        - The argument 'mode' specifies if the request will be with reference to
        a specific status. If 'mode' is None, the request will fetch the most recent
        statuses of the public timeline. If mode is 'subsequent' or 'previous', 
        the method will fetch statuses that are newer or older than the status
        specified by 'min_max_id', respectively.
        - The argument 'min_max_id' specifies the status ID that will be used as
        reference for the request. Depending on the mode, this will be used as 
        the 'min_id' or 'max_id' parameter in the request.
        """

        if mode is None:
            req_url = f"{self.server_url}api/v1/timelines/public?limit={n_statuses}"
        elif mode == "subsequent":
            if min_max_id is None:
                raise ValueError("min_max_id must be specified for subsequent mode")
            req_url = f"{self.server_url}api/v1/timelines/public?limit={n_statuses}&min_id={min_max_id}"
        elif mode == "previous":
            if min_max_id is None:
                raise ValueError("min_max_id must be specified for previous mode")
            req_url = f"{self.server_url}api/v1/timelines/public?limit={n_statuses}&max_id={min_max_id}"
        else:
            raise ValueError("mode must be either None, 'subsequent', or 'previous'")

        if self.token:
            self.response = requests.get(req_url, headers=self.headers)
        else:
            self.response = requests.get(req_url)
        
        self.last_req_type = "timeline"
    
    def req_account_statuses(self, account_id : str, n_statuses : int = 40, 
                             mode : str = None, min_max_id : str = None) -> None:
        """
        This method sends a request to the Mastodon API to fetch statuses from
        a specific account.
        - The argument 'account_id' specifies the account from which the statuses
        will be fetched.
        - The argument 'n_statuses' specifies the number of statuses to fetch,
        and is used as the 'limit' parameter in the request.
        - The argument 'mode' specifies if the request will be with reference to
        a specific status. If 'mode' is None, the request will fetch the most recent
        statuses of the public timeline. If mode is 'subsequent' or 'previous', 
        the method will fetch statuses that are newer or older than the status
        specified by 'min_max_id', respectively.
        - The argument 'min_max_id' specifies the status ID that will be used as
        reference for the request. Depending on the mode, this will be used as 
        the 'min_id' or 'max_id' parameter in the request.
        """

        if mode is None:
            req_url = f"{self.server_url}api/v1/accounts/{account_id}/statuses?limit={n_statuses}"
        elif mode == "subsequent":
            if min_max_id is None:
                raise ValueError("min_id must be specified for subsequent mode")
            req_url = f"{self.server_url}api/v1/accounts/{account_id}/statuses?limit={n_statuses}&min_id={min_max_id}"
        elif mode == "previous":
            if min_max_id is None:
                raise ValueError("max_id must be specified for previous mode")
            req_url = f"{self.server_url}api/v1/accounts/{account_id}/statuses?limit={n_statuses}&max_id={min_max_id}"
        else:
            raise ValueError("mode must be either None, 'subsequent', or 'previous'")

        if self.token:
            self.response = requests.get(req_url, headers=self.headers)
        else:
            self.response = requests.get(req_url)
        
        self.last_req_type = "account_statuses"
    