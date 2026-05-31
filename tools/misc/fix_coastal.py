import re
import csv

# --- Configuration ---
txt_file_path = r'C:\Users\Kahl\Desktop\error.log'
csv_file_path = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\definition.csv'
output_csv_path = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\definition_fixed.csv'

def fix_coastal_disagreements():
    ids_to_toggle = set()
    
    # 1. Extract all the province IDs from the text file
    # We use regex to find the exact number where [id] would be.
    pattern = re.compile(r"province (\d+) is coastal")
    
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
            for line in txt_file:
                if "Bitmap and province definition disagree" in line:
                    match = pattern.search(line)
                    if match:
                        ids_to_toggle.add(match.group(1))
    except FileNotFoundError:
        print(f"Error: Could not find {txt_file_path}")
        return

    print(f"Found {len(ids_to_toggle)} coastal disagreements to fix.")

    # 2. Process the CSV file and toggle the 6th entry (index 5)
    updated_rows = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            # HOI4 standard uses ';' as the delimiter. Change to ',' if yours differs.
            reader = csv.reader(csv_file, delimiter=';') 
            
            for row in reader:
                # Check if the row has enough columns and if the ID matches
                if len(row) >= 6 and row[0] in ids_to_toggle:
                    current_value = row[5].strip().lower()
                    
                    # Toggle true/false
                    if current_value == 'true':
                        row[5] = 'false'
                    elif current_value == 'false':
                        row[5] = 'true'
                        
                updated_rows.append(row)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_file_path}")
        return

    # 3. Write the corrected data to a new file
    with open(output_csv_path, 'w', encoding='utf-8', newline='') as out_file:
        writer = csv.writer(out_file, delimiter=';')
        writer.writerows(updated_rows)

    print(f"Done! The fixed data has been saved to {output_csv_path}")

if __name__ == "__main__":
    fix_coastal_disagreements()