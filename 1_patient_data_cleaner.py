#!/usr/bin/env python3
"""
Patient Data Cleaner

This script standardizes and filters patient records according to specific rules:

Data Cleaning Rules:
1. Names: Capitalize each word (e.g., "john smith" -> "John Smith")
2. Ages: Convert to integers, set invalid ages to 0
3. Filter: Remove patients under 18 years old
4. Remove any duplicate records

Input JSON format:
    [
        {
            "name": "john smith",
            "age": "32",
            "gender": "male",
            "diagnosis": "hypertension"
        },
        ...
    ]

Output:
- Cleaned list of patient dictionaries
- Each patient should have:
  * Properly capitalized name
  * Integer age (≥ 18)
  * Original gender and diagnosis preserved
- No duplicate records
- Prints cleaned records to console

Example:
    Input: {"name": "john smith", "age": "32", "gender": "male", "diagnosis": "flu"}
    Output: {"name": "John Smith", "age": 32, "gender": "male", "diagnosis": "flu"}

Usage:
    python patient_data_cleaner.py
"""

import json
import os

def load_patient_data(filepath):
    """
    Load patient data from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        list: List of patient dictionaries
    """
    # BUG: Previously had no error handling if the JSON file path was incorrect,
    #       which raised a FileNotFoundError and crashed the script.
    # FIX: Wrapped the file-open call in a try/except so the function returns an
    #       empty list and prints a helpful message instead of crashing.
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return []

def clean_patient_data(patients):
    """
    Clean patient data by:
    - Capitalizing names
    - Converting ages to integers
    - Filtering out patients under 18
    - Removing duplicates
    
    Args:
        patients (list): List of patient dictionaries
        
    Returns:
        list: Cleaned list of patient dictionaries
    """
    cleaned_patients = []
    
    for patient in patients:
        # BUG: The original code stored the capitalised name under the wrong key
        #      "nage", causing a KeyError later when the script tried to access
        #      patient['name'].
        # FIX: Capitalise the name correctly and store it back into the existing
        #      'name' field.
        patient['name'] = patient['name'].title()
        
        # BUG: The original code attempted to call the non-existent method
        #      .fill_na on a string and didn't validate numeric conversion.
        # FIX: Safely cast the age to int, defaulting to 0 if conversion fails.
        try:
            patient['age'] = int(patient['age'])
        except ValueError:
            patient['age'] = 0
        
        # BUG: The original comparison used assignment (=) instead of equality
        #      and kept patients *under* 18 instead of filtering them out.
        # FIX: Retain only patients aged 18 or older.
        if patient['age'] >= 18:
            cleaned_patients.append(patient)
    
    # BUG: Duplicate removal previously called a pandas method that doesn't
    #      exist for plain dictionaries, leaving duplicates in the output.
    # FIX: Remove duplicates using a set of tuples representation.
    cleaned_patients = [dict(t) for t in {tuple(d.items()) for d in cleaned_patients}]
    
    # BUG: Function returned None when no valid patients remained, causing
    #      calling code to raise TypeErrors while iterating.
    # FIX: Always return a list (possibly empty) for consistent behaviour.
    return cleaned_patients

def main():
    """Main function to run the script."""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the data file
    data_path = os.path.join(script_dir, 'data', 'raw', 'patients.json')
    
    patients = load_patient_data(data_path)
    
    cleaned_patients = clean_patient_data(patients)
    
    # BUG: Original code assumed cleaned_patients was never None and also used
    #      the wrong key ('nage').
    # FIX: After previous fixes cleaned_patients is always a list and names are
    #      under 'name', so we simply iterate and print if the list is not empty.
    if cleaned_patients:
        # Print the cleaned patient data
        print("Cleaned Patient Data:")
        for patient in cleaned_patients:
            print(f"Name: {patient['name']}, Age: {patient['age']}, Diagnosis: {patient['diagnosis']}")
    
    return cleaned_patients

if __name__ == "__main__":
    main()