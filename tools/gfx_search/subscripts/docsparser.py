import re

def extract_docs_info(file_path):
    function_info = []
    with open(file_path, 'r') as file:
        content = file.read()
        pattern = r'#\s?@docs\((.+?)\):(.+?)(.*?)\n\s*(\w+)\s*='
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            docs_category = match[0].strip()
            docs_description = match[1].strip() + match[2].strip()
            function_name = match[3].strip()
            function_info.append((function_name, docs_category, docs_description))
    return function_info