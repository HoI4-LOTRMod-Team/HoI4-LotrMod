This is a script that automatically converts leader portaits into
"small", advisor portraits.

Usage:
python convert_to_small.py some_folder
will convert all portraits in the gfx/leaders/some_folder folder
and put them inside a gfx/leaders/some_folder/small

The output of the script will correspond to a .gfx file that includes all the definitions.
You can use a redirection/pipe operator to write this directly into the correct file. Example:

python.exe .\convert_to_small.py Elves | Out-File ../../../interface/lotr_characters.gfx -Encoding ASCII