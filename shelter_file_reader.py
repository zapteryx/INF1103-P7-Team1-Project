import csv
import json
from pathlib import Path


class ShelterFileReader:
    REQUIRED_FIELDS = (
    "Category",
    "Shelter Name",
    "Current Occupants",
    "Maximum Capacity",
    "Requirements",
    "Description",
    "Address",
    "Contact"
)
    

