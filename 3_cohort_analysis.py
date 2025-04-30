import polars as pl
import os

def analyze_patient_cohorts(input_file: str) -> pl.DataFrame:
    """
    Analyze patient cohorts based on BMI ranges.
    
    Args:
        input_file: Path to the input CSV file
        
    Returns:
        DataFrame containing cohort analysis results with columns:
        - bmi_range: The BMI range (e.g., "Underweight", "Normal", "Overweight", "Obese")
        - avg_glucose: Mean glucose level by BMI range
        - patient_count: Number of patients by BMI range
        - avg_age: Mean age by BMI range
    """
    parquet_path = "patients_large.parquet"
    # Convert CSV to Parquet for efficient processing (only once)
    if not os.path.exists(parquet_path):
        # Using scan_csv keeps this lazy and memory-efficient
        pl.scan_csv(input_file).sink_parquet(parquet_path)

    # Lazy query for cohort statistics
    # First step: filter outliers and add BMI categories
    df = (
        pl.scan_parquet(parquet_path)
        # Filter BMI in valid range (outliers removed)
        .filter((pl.col("BMI") >= 10) & (pl.col("BMI") <= 60))
        .collect()
    )
    
    # Add BMI category using a concrete approach
    df = df.with_columns([
        pl.when(pl.col("BMI") < 18.5).then("Underweight")
        .when(pl.col("BMI") < 25).then("Normal")
        .when(pl.col("BMI") < 30).then("Overweight")
        .otherwise("Obese")
        .alias("bmi_range")
    ])
    
    # Second step: group and aggregate
    cohort_results = (
        df.group_by("bmi_range")
        .agg([
            pl.col("Glucose").mean().alias("avg_glucose"),
            pl.len().alias("patient_count"),
            pl.col("Age").mean().alias("avg_age")
        ])
    )

    return cohort_results

def main():
    # Input file
    input_file = "patients_large.csv"
    
    # Run analysis
    results = analyze_patient_cohorts(input_file)
    
    # Print summary statistics
    print("\nCohort Analysis Summary:")
    print(results)

if __name__ == "__main__":
    main() 