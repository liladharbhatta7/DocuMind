import os
import pandas as pd
import re

# Define the directory path for the data folder relative to this script.
data_dir = os.path.join(os.path.dirname(__file__), "data")

# Construct full paths for the input and output CSV files.
input_csv_path = os.path.join(data_dir, "document_data.csv")
output_csv_path = os.path.join(data_dir, "processed.csv")

# Load the dataset and remove duplicate rows.
df = pd.read_csv(input_csv_path)
df = df.drop_duplicates()

# Print the columns to verify column names.
print("Columns in CSV:", df.columns.tolist())

# Function to convert Nepali (Devanagari) digits to English digits.
def convert_nepali_digits(text):
    return text.translate(str.maketrans("०१२३४५६७८९", "0123456789"))

# Function to clean and normalize text.
def clean_text(text):
    if pd.isnull(text):
        return ""
    
    text = text.lower()
    
    corrections = {
        "llofficerportal": "officer portal",
        "govnp": "gov.np",
        "nepar": "nepal",
        "commonreportvi": "common reporting",
        "peosperous": "prosperous",
        "i mpden": "independent",
        "qaiezcaeaboiऐ": "",
        "agd": "",
        "nlo.": "no.",
        "our tax is f our own development": "our tax is for our own development",
        "signatureः": "signature",
        "dashrathachanda": "dashrathechanda",
        "cs scanned with camscanner": ""
    }

    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    
    text = convert_nepali_digits(text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\b(?:http|https|www)\S*\b', '', text)
    text = re.sub(r'[^a-zA-Z0-9\u0900-\u097F\s\.:/()\-,]', '', text)
    text = re.sub(r'\b(?:or|with|and|is)\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Determine the column to clean:
# If 'text' or 'content' is not present, use the first column.
if 'text' in df.columns:
    column_to_clean = 'text'
elif 'content' in df.columns:
    column_to_clean = 'content'
else:
    column_to_clean = df.columns[0]
    print(f"Using first column for cleaning: '{column_to_clean}'")

# Apply the cleaning function on the selected column.
df[column_to_clean] = df[column_to_clean].apply(clean_text)

# Save the cleaned data.
df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
print("✅ Data cleaned and saved to", output_csv_path)
