import os
import re

class LocCollection:
    def __init__(self, root_directory):
        """
        Scans the directory and subdirectories for .yml files and extracts
        key-value pairs based on the specific regex pattern.
        """
        self._data = {}
        # The exact regex pattern requested
        self._pattern = re.compile(r'^(\s*)([\w\.\-]+):(\d*)\s*"(.*)"')
        
        self._scan_directory(root_directory)

    def _scan_directory(self, root_directory):
        # Walk through the directory tree
        for root, _, files in os.walk(root_directory):
            for file in files:
                if file.endswith('.yml'):
                    full_path = os.path.join(root, file)
                    self._process_file(full_path)

    def _process_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    match = self._pattern.match(line)
                    if match:
                        # Group 2 is the key ([\w\.\-]+)
                        # Group 4 is the value (.*) inside the quotes
                        key = match.group(2)
                        value = match.group(4)

                        if key in self._data:
                            print(f"Warning: Key '{key}' is being overwritten (found in {filepath} on line {line_num}).")

                        self._data[key] = value
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")

    def get(self, key):
        """Returns the value for the given key, or None if not found."""
        return self._data.get(key)

    def contains(self, key):
        """Returns True if the key exists, False otherwise."""
        return key in self._data