

This script generates masked decision icons from non-masked ones.

Simply put any unmasked images into decisions/unmasked and run this script.

Generates respective .gfx file as output. Make sure to pipe that stuff into the right file.

Usage example:
python.exe .\mask_icons.py | Out-File ../../../../interface/decisions.gfx -Encoding ASCII