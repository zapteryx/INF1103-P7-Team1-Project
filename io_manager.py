import csv
import os

filename = "singapore_shelters_directory.csv"

def load_shelters_from_csv (filepath: str = filename) -> list:
    #Reads shelter data directly from CSV into a list of dictionaries.
    if not os.path.exists(filepath):
        print("\nFile not found:", filepath) # the built-in os module that checks the path stored in filepath
        return []

    shelters = []

   