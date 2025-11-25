import re

class LocFile:
    def __init__(self, filepath=None):
        self.lines = [] # Stores the actual lines of the file
        self.key_map = {} # Maps "key_name" to the line number index
        self.indent = " " # Default indentation
        
        if filepath:
            self.load(filepath)

    def load(self, filepath):
        """Loads the file and builds an index of keys."""
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            self.lines = f.readlines()
            
        # Regex to find keys: looks for text followed by :digit and a quoted string
        # Group 1: Indentation, Group 2: Key, Group 3: Version, Group 4: Value
        self.pattern = re.compile(r'^(\s*)([\w\.\-]+):(\d+)\s*"(.*)"')
        
        self.key_map = {}
        for index, line in enumerate(self.lines):
            match = self.pattern.match(line)
            if match:
                # We store the key as "key_name:version" (e.g., "key_0:0")
                full_key = f"{match.group(2)}"
                self.key_map[full_key] = index
                # Detect indentation style from first match
                if self.indent == " ": 
                    self.indent = match.group(1)

    def get(self, key):
        """Returns the string value for a key."""
        if key in self.key_map:
            index = self.key_map[key]
            match = self.pattern.match(self.lines[index])
            if match:
                return match.group(4)
        return None

    def set(self, key, value):
        """Updates an existing key with a new value."""
        if key in self.key_map:
            index = self.key_map[key]
            current_line = self.lines[index]
            match = self.pattern.match(current_line)
            if match:
                # Reconstruct the line preserving indentation and key version
                # match.group(1) is indent, group(2) is key name, group(3) is version
                new_line = f'{match.group(1)}{match.group(2)}:{match.group(3)} "{value}"\n'
                self.lines[index] = new_line
        else:
            print(f"Key '{key}' not found. Use add() for new keys.")

    def add(self, key_full, value):
        """Adds a new key to the end of the file inside the block."""
        # key_full should be "key_name:0"
        if key_full in self.key_map:
            print(f"Key {key_full} already exists. Updating instead.")
            self.set(key_full, value)
            return

        # Construct the new line
        new_line = f'\n{self.indent}{key_full}:0 "{value}"'
        
        # Insert before the last line if it's empty, or append
        # We try to stay inside the l_english block
        self.lines.append(new_line)
        self.key_map[key_full] = len(self.lines) - 1

    def save(self, filepath):
        """Writes the modified lines back to a file."""
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.writelines(self.lines)
