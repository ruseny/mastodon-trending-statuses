"""
This module creates an app to access mastodon.social,
gets credentials and an authorisation token 
that will be used to fetch data. The credentials and 
the token are written in a text file accessible by 
other modules. 

Ideally this module should be used only once at the 
beginning of the project.
"""

# Dependencies
import requests
import json
import os

# URL components for requests
app_create_dir = "/api/v1/apps"
token_dir = "/oauth/token"
verify_dir = "/api/v1/apps/verify_credentials"

# A class with methods to create the app and get credentials and token
class MastodonApp:
    """
    This class can be used to create a new app that 
    can get data from mastodon.social. 
    The class attributes hold basic information
    such as credentials and authorisation token.
    Methods can create an app, get credentials and
    authorisation token, and write these to a file.
    To create an instance of the class, a name should
    be given to the app. The Mastodon server can also be
    specified; the default is 'mastodon.social'.
    """

    def __init__(self, app_name: str, server: str = "mastodon.social") -> None:
        self.app_name = app_name
        self.server = server
        self.base_url = f"https://{self.server}"
        self.credentials = {}
        self.token = ""
        self.verification = "Not verified yet"
    
    def create_app(self):
        """
        This method sends a request to mastodon.social
        to create the app and stores credentials if the
        request is successful.
        """
        resp = requests.post(
            self.base_url + app_create_dir, 
            data = {
                "client_name" : self.app_name, 
                "redirect_uris" : "urn:ietf:wg:oauth:2.0:oob"
            }
        )
        if resp.status_code == 200:
            print("Response status 200: request successful")
            self.credentials = resp.json()
        else:
            print("Response status not 200: request failed")
    
    def get_token(self):
        """
        This method gets the authorisation token if 
        the credentials are already stored.
        """
        if self.credentials == {}:
            print("The dictionary of credentials is empty.")
        elif self.credentials["client_id"] is None:
            print("Client ID is missing.")
        elif self.credentials["client_secret"] is None:
            print("Client secret is missing.")
        else:
            resp = requests.post(
                self.base_url + token_dir, 
                data = {
                    "grant_type" : "client_credentials", 
                    "client_id" : self.credentials["client_id"], 
                    "client_secret" : self.credentials["client_secret"], 
                    "redirect_uri" : "urn:ietf:wg:oauth:2.0:oob"
                }
            )
            if resp.status_code == 200:
                print("Response status 200: request successful")
                token_dict = resp.json()
                self.token = token_dict["access_token"]
            else: 
                print("Response status not 200: request failed")
    
    def write_credentials(self, file_path=None):
        """
        This method writes the credential to a text file.
        Arg: file_path specifies where the file should be saved,
        including file name. The directory should already exist. 
        If None, the file will be saved in the directory 
        '../credentials' with file name mastodon_credentials.txt.
        """
        if file_path is None:
            if not os.path.exists("../credentials"):
                os.mkdir("../credentials")
            with open("../credentials/mastodon_credentials.txt", "w") as text_file:
                json.dump(self.credentials, text_file)
        else:
            with open(file_path, "w") as text_file:
                json.dump(self.credentials, text_file)
    
    def write_token(self, file_path=None):
        """
        This method writes the authorisation token to a text file.
        Arg: file_path specifies where the file should be saved,
        including file name. If None, the file will be saved in the 
        working directory with name auth_token.txt.
        """
        if file_path is None:
            if not os.path.exists("../credentials"):
                os.mkdir("../credentials")
            with open("../credentials/app_token.txt", "w") as text_file:
                json.dump(self.token, text_file)
        else:
            with open(file_path, "w") as text_file:
                json.dump(self.token, text_file)

    def verify_app(self):
        """
        This method can be used to verify that app creation and
        authorisation steps have been successfully completed.
        """
        resp = requests.get(
            self.base_url + verify_dir, 
            headers = {
                "Authorization" : f"Bearer {self.token}"
            }
        )
        if resp.status_code == 200:
            print("Response status 200: verification successful")
            self.verification = "Successfully verified"
        else: 
            print("Response status not 200: verification failed")
            self.verification = "Verification failed"

