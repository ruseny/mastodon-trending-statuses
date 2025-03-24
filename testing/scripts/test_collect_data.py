"""
This script is designed to test the collect_data.py script
with a small data size.
"""

# Dependencies
from datetime import datetime

# Define path to original scripts
import sys
sys.path.append("../../")

# Import building blocks of the script
from scripts.collect_data import (
    prep_dirs, 
    check_app_token, 
    get_trending, 
    get_adjacent, 
    save_raw_and_processed
)

# Parameters for testing
# Small data size for quick operation
MAX_BATCHES = 3
N_PER_BATCH = 20

# Run the script with given parameters
if __name__ == "__main__":
    
    # prep
    prep_dirs()
    app_token = check_app_token()

    # trending
    time_stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    trending_statuses = get_trending(app_token = app_token, max_batches = MAX_BATCHES, n_per_batch = N_PER_BATCH)
    save_raw_and_processed(trending_statuses, "trending_statuses", time_stamp)

    # adjacent, run for each mode and focus, name accordingly
    for mode in ["previous", "subsequent"]:
        for focus in ["no", "yes"]:
            type_name = f"adjacent_statuses_{mode}_acc_focus_{focus}"
            adjacent_statuses = get_adjacent(reference = trending_statuses, mode = mode, focus_accounts = focus)
            save_raw_and_processed(adjacent_statuses, type_name, time_stamp)