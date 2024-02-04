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

# Replace 'your_code_file.txt' with the path to your actual code file
input_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\moria.txt'
reformat_code(input_file)
input_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\erebor.txt'
reformat_code(input_file)
input_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\rivendell.txt'
reformat_code(input_file)
input_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\isengard.txt'
reformat_code(input_file)
input_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\mirkwood.txt'
reformat_code(input_file)