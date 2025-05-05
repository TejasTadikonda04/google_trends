import pandas as pd

def extract_data(filepath='actualDataTeamProject.csv'):
    print(f"Reading data from {filepath}...")
    df = pd.read_csv(filepath)
    return df

if __name__ == "__main__":
    df = extract_data()
    print(f"Extracted {len(df)} rows.")
