import re

# Define the file path
file_path = r"C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\units\equipment\infantry.txt"

# Define the factor to multiply with
factor = 1.4

# Read the file content
with open(file_path, 'r') as file:
    content = file.read()

# Find and replace occurrences of "build_cost_ic = [X]"
pattern = r"build_cost_ic = (\d+(\.\d+)?)"
replaced_content = re.sub(pattern, lambda match: f"build_cost_ic = {float(match.group(1)) * factor:.2f}", content)

# Write the modified content back to the file
with open(file_path, 'w') as file:
    file.write(replaced_content)