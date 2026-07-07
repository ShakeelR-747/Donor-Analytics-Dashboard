import pandas as pd
import re

# ----------------------------
# File Name
# ----------------------------
INPUT_FILE = "for-upload (1).xlsx"
OUTPUT_FILE = "Cleaned_Donors.xlsx"
REPORT_FILE = "Data_Cleaning_Report.txt"

# ----------------------------
# Read Excel Sheets
# ----------------------------
new_donors = pd.read_excel(INPUT_FILE, sheet_name="NEW-DONORS")
existing_donors = pd.read_excel(INPUT_FILE, sheet_name="EXISTING-DONORS")

# ----------------------------
# Cleaning Function
# ----------------------------
def clean_dataset(df, sheet_name):

    report = []
    report.append(f"\n{'='*60}")
    report.append(f"{sheet_name}")
    report.append(f"{'='*60}")

    original_rows = len(df)
    original_columns = len(df.columns)

    # ----------------------------
    # Clean Column Names
    # ----------------------------
    df.columns = df.columns.astype(str)
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace("\n", " ", regex=False)

    # Remove duplicate column names
    df = df.loc[:, ~df.columns.duplicated()]

    # ----------------------------
    # Remove Empty Columns
    # ----------------------------
    empty_columns = df.columns[df.isnull().all()].tolist()

    report.append(f"\nEmpty Columns Removed : {len(empty_columns)}")

    df.dropna(axis=1, how='all', inplace=True)

    # ----------------------------
    # Remove Duplicate Rows
    # ----------------------------
    duplicates = df.duplicated().sum()

    report.append(f"Duplicate Rows Removed : {duplicates}")

    df.drop_duplicates(inplace=True)

    # ----------------------------
    # Remove Extra Spaces
    # ----------------------------
    object_columns = df.select_dtypes(include="object").columns

    for col in object_columns:
        df[col] = df[col].astype(str).str.strip()

    # ----------------------------
    # Clean Email
    # ----------------------------
    email_columns = [c for c in df.columns if "mail" in c.lower() or "email" in c.lower()]

    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    for col in email_columns:

        df[col] = df[col].astype(str).str.lower().str.strip()

        invalid = (~df[col].str.match(email_regex)) & (df[col] != "nan")

        report.append(f"Invalid Emails in {col} : {invalid.sum()}")

    # ----------------------------
    # Clean Mobile Numbers
    # ----------------------------
    mobile_columns = [c for c in df.columns if "mobile" in c.lower()]

    for col in mobile_columns:

        df[col] = df[col].astype(str)

        df[col] = df[col].str.replace(r"\D", "", regex=True)

        invalid = (~df[col].str.match(r'^\d{10}$')) & (df[col] != "")

        report.append(f"Invalid Mobile Numbers in {col} : {invalid.sum()}")

    # ----------------------------
    # Clean PAN Numbers
    # ----------------------------
    pan_columns = [c for c in df.columns if "pan" in c.lower()]

    pan_regex = r'^[A-Z]{5}[0-9]{4}[A-Z]$'

    for col in pan_columns:

        df[col] = df[col].astype(str).str.upper().str.strip()

        invalid = (~df[col].str.match(pan_regex)) & (df[col] != "NAN")

        report.append(f"Invalid PAN Numbers in {col} : {invalid.sum()}")

    # ----------------------------
    # Convert Date Columns
    # ----------------------------
    date_columns = [c for c in df.columns if "date" in c.lower()]

    for col in date_columns:

        df[col] = pd.to_datetime(df[col], errors="coerce")

    # ----------------------------
    # Numeric Columns
    # ----------------------------
    amount_columns = [c for c in df.columns if "amount" in c.lower()]

    for col in amount_columns:

        df[col] = pd.to_numeric(df[col], errors="coerce")

        negative = (df[col] < 0).sum()

        report.append(f"Negative Amounts in {col} : {negative}")

    # ----------------------------
    # Missing Values
    # ----------------------------
    report.append("\nMissing Values")

    missing = df.isnull().sum()

    for col, value in missing.items():

        if value > 0:
            report.append(f"{col} : {value}")

    # ----------------------------
    # Final Summary
    # ----------------------------
    report.append("\nSummary")

    report.append(f"Original Rows : {original_rows}")
    report.append(f"Rows After Cleaning : {len(df)}")

    report.append(f"Original Columns : {original_columns}")
    report.append(f"Columns After Cleaning : {len(df.columns)}")

    return df, report

# ----------------------------
# Clean Both Sheets
# ----------------------------
new_donors, report1 = clean_dataset(new_donors, "NEW-DONORS")
existing_donors, report2 = clean_dataset(existing_donors, "EXISTING-DONORS")

# ----------------------------
# Save Cleaned Excel
# ----------------------------
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:

    new_donors.to_excel(writer,
                        sheet_name="NEW-DONORS",
                        index=False)

    existing_donors.to_excel(writer,
                             sheet_name="EXISTING-DONORS",
                             index=False)

# ----------------------------
# Save Report
# ----------------------------
with open(REPORT_FILE, "w", encoding="utf-8") as f:

    for line in report1:
        f.write(line + "\n")

    f.write("\n")

    for line in report2:
        f.write(line + "\n")

print("="*50)
print("Cleaning Completed Successfully")
print("="*50)
print("Cleaned File :", OUTPUT_FILE)
print("Report File  :", REPORT_FILE)