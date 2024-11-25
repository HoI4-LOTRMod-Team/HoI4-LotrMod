import re

def parse_loading_tips(file_path):
    # Regular expression pattern to match LOADING_TIP_X:0 "Quote"
    pattern = r'LOADING_TIP_\d+:\d+\s+"(.*?)"'
    
    # Set to store unique quotes
    unique_quotes = set()
    
    # List to store the final filtered quotes
    filtered_quotes = []

    # Read file and find all matching loading tips
    with open(file_path, 'r') as file:
        content = file.read()
        matches = re.findall(pattern, content, re.DOTALL)
        
        # Add only unique quotes to the filtered list
        for match in matches:
            if match not in unique_quotes:
                unique_quotes.add(match)
                filtered_quotes.append(match)
    
    # Print the quotes with sequential numbering
    for i, quote in enumerate(filtered_quotes):
        print(f'LOADING_TIP_{i}:0 "{quote}"')

# Example usage
file_path = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\localisation\english\loading_tips_l_english.yml'
parse_loading_tips(file_path)
