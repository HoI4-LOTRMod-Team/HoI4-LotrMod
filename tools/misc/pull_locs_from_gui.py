import re

def process_instant_text_boxes(input_file):
    pattern = re.compile(r'instantTextBoxType\s*=\s*{((?:[^{}]*\{[^{}]*\}[^{}]*)*)}', re.DOTALL)
    replacements = []

    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = pattern.findall(content)

        for match in matches:
            name_match = re.search(r'name\s*=\s*\"([^\"]+)\"', match)
            text_match = re.search(r'text\s*=\s*\"([^\"]+)\"', match)

            if name_match and text_match:
                name = name_match.group(1)
                text = text_match.group(1)

                # Skip if text is an integer, "lol boat", or "Happy-Go-Lucky-Tank"
                if text.isdigit() or text == "lol boat" or text == "Happy-Go-Lucky-Tank":
                    continue

                print(f"Name: {name}")
                print(f"Text: {text}")

                confirmation = input("Do you want to replace the text? (y/n): ").lower()
                if confirmation == 'y':
                    # Perform the replacement in the original content
                    content = re.sub(f'text\s*=\s*\"{re.escape(text)}\"', f'text = "{name}"', content)

                    # Add to replacements list
                    replacements.append(f'{name}:0 "{text}"')

    # Output the list of processed occurrences
    print("\nProcessed occurrences:")
    for replacement in replacements:
        print(replacement)

    # Write the modified content back to the file
    with open(input_file, 'w', encoding='utf-8') as file:
        file.write(content)

# Example usage:
# Assuming your input file is named 'input.txt'
input_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\interface\countrytechtreeview.gui'
process_instant_text_boxes(input_file)
