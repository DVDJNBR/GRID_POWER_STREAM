import pandas as pd

excel_path = "RESOURCES/ref_data_engineer.xlsx"
sheets = [
    "B1 Pilotage C1-C7 (E1, E2 et E3",
    "B2 API REST C8-12 (E4)",
    "B3 Data warehouse C13-C17 (E5-E",
    "B4 Data lake C18-C21 (E7)",
]

with pd.ExcelFile(excel_path) as xls:
    for sheet in sheets:
        print(f"\n--- Sheet: {sheet} ---")
        df = pd.read_excel(xls, sheet_name=sheet)
        print("Columns:", df.columns.tolist())
        print("\nFirst 10 rows:")
        print(df.iloc[:10, :])
