"""
This script creates an app on mastodon.social, 
gets an authorisation token for the app, 
verifies the app, and writes the token to a file.
"""

import os
from datetime import datetime
import sys
sys.path.append('../')

from src.app_setup import MastodonApp

if __name__ == "__main__":

    # Create an app
    app = MastodonApp(app_name = "mastodon_trending_statuses")
    app.create_app()
    # Get token
    app.get_token()
    # Verify app
    app.verify_app()
    # If verified, write token
    if app.verification == "Successfully verified":
        if os.path.exists("../credentials/app_token.txt"):
            print("File app_token.txt already exists. Adding timestamp to file name.")
            file_path = f"../credentials/app_token_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            app.write_token(file_path)
            print("Authorisation token written to file:", file_path)
        elif os.path.exists("../credentials"):
            file_path = "../credentials/app_token.txt"
            app.write_token(file_path)
            print("Authorisation token written to file:", file_path)
        else:
            print("Creating directory '../credentials'")
            os.mkdir("../credentials")
            file_path = "../credentials/app_token.txt"
            app.write_token(file_path)
            print("Authorisation token written to file:", file_path)
    else:
        print("Authorisation token not written to file because verification failed.")