
from state import *
import csv
import os

# This is a bonus script that uses some of nudge2's dependencies but isn't connected. Can be removed.
# Goes through adjacencies and removes any impassable ones where one or two provinces are inside an impassable state

states = get_all_states()
impassable_states = []


for st in states:
    if st.is_impassable:
        impassable_states.append(st)


def is_valid(pfrom, pto):
    for st in impassable_states:
        if pfrom in st.province_list or pto in st.province_list:
            return False
    return True


adj_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\adjacencies.csv'



def process_csv(path):
    temp_rows = []
    header = None

    # --- READ PHASE ---
    try:
        with open(path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter=';')
            
            # Save the header to write it back later (optional)
            try:
                header = next(reader)
            except StopIteration:
                print("File is empty.")
                return

            # Iterate through rows
            for row in reader:
                # Ensure row has at least 2 columns to avoid IndexError
                if len(row) >= 2 and row[2]=="impassable":
                    # Pass the first two entries to the validation function
                    if is_valid(int(row[0]), int(row[1])):
                        temp_rows.append(row)
                    else:
                        print("Removed adj")
                else:
                    temp_rows.append(row)
                    
    except FileNotFoundError:
        print(f"Error: The file {path} was not found.")
        return

    # --- WRITE PHASE ---
    # Overwrite the original file
    with open(path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        
        # Write header back first
        if header:
            writer.writerow(header)
            
        # Write the valid rows
        writer.writerows(temp_rows)
        
    print(f"Successfully processed {path}")


process_csv(adj_file)