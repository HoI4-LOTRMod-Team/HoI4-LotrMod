import re
import signal
import sys

file1_path = "CelebrationEvents.txt"
file2_path = "C:\\Users\\Kahl\\Documents\\Paradox Interactive\\Hearts of Iron IV\\mod\\lotr\\localisation\\english\\lothlorien\\celebration_events_l_english.yml"

content1 = ""

def save_and_exit(signum, frame):
    global content1

    print("\nCtrl+C detected. Saving the changes and exiting...")
    with open(file1_path, "w") as f1:
        f1.write(content1)
    sys.exit(0)

def main():
    global content1

    signal.signal(signal.SIGINT, save_and_exit)

    # Step 1: Find instances of "name = celebrations.X.a" in file1
    pattern = r"name = celebrations\.(\d{5})\.a"
    with open(file1_path, "r") as f1:
        content1 = f1.read()
    
    matches = re.finditer(pattern, content1)

    for match in matches:
        celebration_number = match.group(1)
        key_to_find = f"celebrations.{celebration_number}.d"

        # Step 2: Look for the key in file2 and output its contents
        with open(file2_path, "r") as f2:
            content2 = f2.read()
        
        start_index = content2.find(key_to_find)
        if start_index != -1:
            end_index = content2.find("\n", start_index)
            if end_index != -1:
                value = content2[start_index:end_index].strip()
                print("Value for", key_to_find, "in file2.yml:\n\n", value)

                # Step 3: Wait for user to copy-paste content
                print("\nCopy-paste the content (Type 'e' on a line to finish):")
                copy_pasted_lines = []
                while True:
                    line = "\t\t"+input()
                    if line.strip() == "e":
                        break
                    copy_pasted_lines.append(line)

                copy_pasted_content = "\n".join(copy_pasted_lines)

                # Step 4: Add the copy-pasted content to file1
                replacement = f"name = celebrations.{celebration_number}.a\n{copy_pasted_content}"
                content1 = re.sub(match.group(0), replacement, content1)

    # Write the updated content back to file1
    with open(file1_path, "w") as f1:
        f1.write(content1)

if __name__ == "__main__":
    main()
