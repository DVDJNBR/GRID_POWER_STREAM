import pandas as pd
import os
import re

excel_path = "RESOURCES/ref_data_engineer.xlsx"
output_path = "CONTEXT/COMPETENCES.md"

sheets_to_extract = [
    "B1 Pilotage C1-C7 (E1, E2 et E3",
    "B2 API REST C8-12 (E4)",
    "B3 Data warehouse C13-C17 (E5-E",
    "B4 Data lake C18-C21 (E7)",
]


def clean_text(text):
    if pd.isna(text):
        return ""
    return str(text).strip()


def parse_criteria(text):
    if not text:
        return []

    # Split by newlines
    lines = [t.strip() for t in text.split("\n") if t.strip()]

    # Heuristic: join lines that are probably continuations
    # If a line starts with a lowercase letter or doesn't start with common markers/numbers,
    # and the previous line doesn't end with a period/colon, join them.

    refined_criteria = []
    if not lines:
        return []

    current_crit = lines[0]
    for i in range(1, len(lines)):
        line = lines[i]
        # If it starts with a dash, bullet, or number, it's definitely a new point
        if re.match(r"^[\-\*•\d\.]", line):
            refined_criteria.append(current_crit)
            current_crit = line
        # If the previous line doesn't end with a terminal punctuation, join
        elif not current_crit.endswith((".", ":", "!", "?")):
            current_crit += " " + line
        else:
            refined_criteria.append(current_crit)
            current_crit = line

    refined_criteria.append(current_crit)
    return refined_criteria


markdown_content = "# Compétences Visées - GRID_POWER_STREAM\n\n"
markdown_content += "> Ce document récapitule les compétences E1, E2, E3, E4, E5 et E7 sous forme hiérarchique.\n\n"

with pd.ExcelFile(excel_path) as xls:
    for sheet_name in sheets_to_extract:
        print(f"Processing sheet: {sheet_name}")
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Identify columns
        col_block = df.columns[0]
        col_comp = (
            "Competence"
            if "Competence" in df.columns
            else ("Competences" if "Competences" in df.columns else df.columns[1])
        )
        col_crit = (
            "CRITÈRES D'ÉVALUATION"
            if "CRITÈRES D'ÉVALUATION" in df.columns
            else df.columns[2]
        )

        for _, row in df.iterrows():
            block_val = clean_text(row[col_block])
            comp_val = clean_text(row[col_comp])
            crit_val = clean_text(row[col_crit])

            # Update current block if found
            if block_val and ("E" in block_val or "Bloc" in block_val):
                if "E6 :" in block_val:  # Explicitly skip E6
                    current_block = "SKIP"
                else:
                    current_block = block_val
                    markdown_content += f"# {current_block}\n\n"

            if current_block == "SKIP":
                continue

            # Update current competence if found
            if comp_val:
                markdown_content += f"## {comp_val}\n\n"
                markdown_content += "### Critères d'évaluation :\n"

            # Add criteria if found
            if crit_val:
                crit_list = parse_criteria(crit_val)
                for c in crit_list:
                    # Clean up the criterion if it already has a bullet
                    c_clean = re.sub(r"^[\-\*•]\s*", "", c)
                    markdown_content += f"- {c_clean}\n"
                markdown_content += "\n"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print(f"Extraction complete. Results saved to {output_path}")
