"""
This script is desinged to run the collect_data.py script on
data collected for testing purposes.
"""

# Define path to original scripts
import sys
sys.path.append("../../")

# Import the main function
from scripts.clean_data import main

# Run the main function
if __name__ == "__main__":
    main()