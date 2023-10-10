@echo off
set /p input_string="Enter the folder in gfx/leaders to process: "

rem Construct the Python command
set "python_command=python.exe .\make_gfx.py -s leaders -o leaders/lotr_leaders_%input_string% %input_string%"

rem Execute the Python command
%python_command%

echo Task completed.
pause