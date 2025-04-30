#!/usr/bin/env python3
"""
Emergency Room Medication Calculator

This script calculates medication dosages for emergency room patients based on 
standard emergency protocols. It follows weight-based dosing guidelines for common 
emergency medications.

Dosing Formula:
    Base Dosage (mg) = Patient Weight (kg) × Medication Factor (mg/kg)
    Loading Dose (mg) = Base Dosage × 2 (for first dose only)

When to use Loading Doses:
    - Only for first doses of certain medications (e.g., antibiotics, anti-seizure meds)
    - Determined by 'is_first_dose' flag in the input
    - Some medications always use loading doses for first administration

Example:
    Patient: 70kg, Medication: epinephrine, Is First Dose: No
    Base Dosage = 70 kg × 0.01 mg/kg = 0.7 mg
    Final Dosage = 0.7 mg

    Patient: 70kg, Medication: amiodarone, Is First Dose: Yes
    Base Dosage = 70 kg × 5 mg/kg = 350 mg
    Loading Dose = 350 mg × 2 = 700 mg
    Final Dosage = 700 mg

Input Format:
    {
        "name": "John Smith",
        "weight": 70.0,
        "medication": "epinephrine",
        "condition": "anaphylaxis",
        "is_first_dose": false,
        "allergies": ["penicillin"]
    }

Output:
    {
        "name": "John Smith",
        "weight": 70.0,
        "medication": "epinephrine",
        "base_dosage": 0.7,
        "is_first_dose": false,
        "loading_dose_applied": false,
        "final_dosage": 0.7,
        "warnings": ["Monitor for arrhythmias"]
    }

Medication Factors (mg/kg):
    epinephrine:  0.01  (Anaphylaxis)
    amiodarone:   5.00  (Cardiac arrest)
    lorazepam:    0.05  (Seizures)
    fentanyl:     0.001 (Pain)
    ...
"""

import json
import os

# Dosage factors for different medications (mg per kg of body weight)
# These are standard dosing factors based on medical guidelines
DOSAGE_FACTORS = {
    "epinephrine": 0.01,  # Anaphylaxis
    "amiodarone": 5.00,   # Cardiac arrest
    "lorazepam": 0.05,    # Seizures
    "fentanyl": 0.001,    # Pain
    "lisinopril": 0.5,    # ACE inhibitor for blood pressure
    "metformin": 10.0,    # Diabetes medication
    "oseltamivir": 2.5,   # Antiviral for influenza
    "sumatriptan": 1.0,   # Migraine medication
    "albuterol": 0.1,     # Asthma medication
    "ibuprofen": 5.0,     # Pain/inflammation
    "sertraline": 1.5,    # Antidepressant
    "levothyroxine": 0.02 # Thyroid medication
}

# Medications that use loading doses for first administration
# BUG: Missing commas between list items and misspelled "fentanyl", causing the
#       three strings to concatenate and the misspelled drug to go unnoticed.
# FIX: Added commas and corrected spelling to ensure each entry is separate and
#       matches the keys used elsewhere.
LOADING_DOSE_MEDICATIONS = [
    "amiodarone",
    "lorazepam",
    "fentanyl",
]

def load_patient_data(filepath):
    """
    Load patient data from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        list: List of patient dictionaries
    """
    # BUG: No error handling for file not found which crashed the script if the
    #       meds.json file was missing.
    # FIX: Wrapped the open call in try/except and return an empty list if the
    #       file is absent so the caller can handle it gracefully.
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found. No patients loaded.")
        return []

def calculate_dosage(patient):
    """
    Calculate medication dosage for a patient.
    
    Args:
        patient (dict): Patient dictionary with 'weight', 'medication', and 'is_first_dose' keys
        
    Returns:
        dict: Patient dictionary with added dosage information
    """
    # Create a copy of the patient data to avoid modifying the original
    patient_with_dosage = patient.copy()
    
    # Extract patient information safely
    # BUG: Accessed keys directly which raised KeyError when missing.
    # FIX: Use .get with defaults and validate.
    weight = float(patient.get('weight', 0))
    medication = str(patient.get('medication', '')).lower()
    if not medication:
        raise ValueError("Medication field is required.")
    
    # Get the medication factor
    # BUG: Added 's' to medication name for lookup, breaking factor retrieval.
    # FIX: Use medication name directly; default to 0 if not found.
    factor = DOSAGE_FACTORS.get(medication, 0)
    
    # Calculate base dosage
    # BUG: Used addition instead of multiplication for dosage calculation.
    # FIX: Correct formula is weight * factor.
    base_dosage = weight * factor
    
    # Determine if loading dose should be applied
    # BUG: Potential missing key; addressed above with .get default.
    is_first_dose = bool(patient.get('is_first_dose', False))
    loading_dose_applied = False
    final_dosage = base_dosage
    
    # Apply loading dose correctly when appropriate
    # BUG: Original code used incorrect list (fixed earlier) and addition.
    # FIX: Multiply base_dosage by 2 to apply loading dose.
    if is_first_dose and medication in LOADING_DOSE_MEDICATIONS:
        loading_dose_applied = True
        final_dosage = base_dosage * 2
    
    # Add dosage information to the patient record
    patient_with_dosage['base_dosage'] = base_dosage
    patient_with_dosage['loading_dose_applied'] = loading_dose_applied
    patient_with_dosage['final_dosage'] = final_dosage
    
    # Add warnings based on medication
    warnings = []
    # BUG: Medication names misspelled, preventing warnings.
    # FIX: Compare against correct names.
    if medication == "epinephrine":
        warnings.append("Monitor for arrhythmias")
    elif medication == "amiodarone":
        warnings.append("Monitor for hypotension")
    elif medication == "fentanyl":
        warnings.append("Monitor for respiratory depression")
    
    patient_with_dosage['warnings'] = warnings
    
    return patient_with_dosage

def calculate_all_dosages(patients):
    """
    Calculate dosages for all patients and sum the total.
    
    Args:
        patients (list): List of patient dictionaries
        
    Returns:
        tuple: (list of patient dicts with dosages, total medication needed)
    """
    total_medication = 0
    patients_with_dosages = []
    
    # Process all patients
    for patient in patients:
        # Calculate dosage for this patient
        patient_with_dosage = calculate_dosage(patient)
        
        # Add to our list
        patients_with_dosages.append(patient_with_dosage)
        
        # Add to total medication
        # BUG: No check if 'final_dosage' key exists. Fixed because
        #       calculate_dosage always adds the key.
        total_medication += patient_with_dosage['final_dosage']
    
    return patients_with_dosages, total_medication

def main():
    """Main function to run the script."""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the data file
    data_path = os.path.join(script_dir, 'data', 'meds.json')
    
    # BUG: No error handling when load_patient_data returned an empty list.
    # FIX: Exit early if no patients to process.
    patients = load_patient_data(data_path)
    if not patients:
        print("No patient data to process.")
        return [], 0.0
    
    # Calculate dosages for all patients
    patients_with_dosages, total_medication = calculate_all_dosages(patients)
    
    # Print the dosage information
    print("Medication Dosages:")
    for patient in patients_with_dosages:
        # BUG: Original code assumed 'name' key always existed.
        # FIX: Use get with fallback.
        print(
            f"Name: {patient.get('name', 'Unknown')}, Medication: {patient['medication']}, "
            f"Base Dosage: {patient['base_dosage']:.2f} mg, "
            f"Final Dosage: {patient['final_dosage']:.2f} mg"
        )
        if patient['loading_dose_applied']:
            print(f"  * Loading dose applied")
        if patient['warnings']:
            print(f"  * Warnings: {', '.join(patient['warnings'])}")
    
    print(f"\nTotal medication needed: {total_medication:.2f} mg")
    
    # Return the results (useful for testing)
    return patients_with_dosages, total_medication

if __name__ == "__main__":
    main()