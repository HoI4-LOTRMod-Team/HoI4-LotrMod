def reformat_code(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    indentation_level = 0
    formatted_lines = []

    for line in lines:
        if line.strip():
            stripped_line = line.lstrip()  # Remove leading whitespace

            # Adjust indentation level
            indentation_level_temp = indentation_level
            if stripped_line.startswith('}'):
                indentation_level_temp -= 1

            # Apply new indentation
            new_line = '\t' * indentation_level_temp + stripped_line
            formatted_lines.append(new_line)

            # Check for opening braces after writing the line
            indentation_level += stripped_line.count('{') - stripped_line.count('}')
        else:
            # Preserve empty lines
            formatted_lines.append('\n')

    # Write the formatted code back to the file
    with open(file_path, 'w') as file:
        file.writelines(formatted_lines)


def get_indentation(text, index):
    if index < 0 or index >= len(text):
        raise ValueError("Index is out of bounds")

    line_start = text.rfind('\n', 0, index) + 1
    line_end = text.find('\n', index)
    if line_end == -1:
        line_end = len(text)

    line = text[line_start:line_end]

    indentation = ''
    for char in line:
        if char in (' ', '\t'):
            indentation += char
        else:
            break

    return indentation

def find_opening_brace(text, closing_brace_index):
    if text[closing_brace_index] != '}':
        raise ValueError("The character at the given index is not a closing brace '}'")

    stack = 0

    for i in range(closing_brace_index, -1, -1):
        if text[i] == '}':
            stack += 1
        elif text[i] == '{':
            stack -= 1

        if stack == 0:
            return i

    raise ValueError("No corresponding opening brace '{' found")

def find_first_valid_closing_brace(text):
    for i, char in enumerate(text):
        if char == '}':
            opening_brace_index = find_opening_brace(text, i)
            opening_brace_line_start = text.rfind('\n', 0, opening_brace_index) + 1
            closing_brace_line_start = text.rfind('\n', 0, i) + 1

            # Check if the opening brace is on the same line as the closing brace
            if opening_brace_line_start == closing_brace_line_start:
                continue

            # Check if the closing brace is the first non-whitespace/tab character on its line
            if text[closing_brace_line_start:i].strip() == '':
                continue

            return i

    return -1

def adjust_closing_brace_indentation(text):
    while True:
        closing_brace_index = find_first_valid_closing_brace(text)
        if closing_brace_index == -1:
            break

        opening_brace_index = find_opening_brace(text, closing_brace_index)
        indentation = get_indentation(text, opening_brace_index)

        text = text[:closing_brace_index] + '\n' + indentation + text[closing_brace_index:]

        #print(text)
        #input()

    return text

def reformat_braces(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    adjusted_content = adjust_closing_brace_indentation(content)

    with open(file_path, 'w') as file:
        file.write(adjusted_content)


# Replace 'your_code_file.txt' with the path to your actual code file
input_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\ai_templates\lotr_generic_infantry.txt'
reformat_code(input_file)
reformat_braces(input_file)