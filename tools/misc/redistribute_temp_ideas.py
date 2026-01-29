


from pdx_parser import *
import os.path
from fix_code_format import *




input_file = "common/ideas/TEMP.txt"

categories = ParseListFromFile_asPObj(input_file).Get("ideas")

handled_files = []
for cat in categories.value:
    for idea in cat.value:
        out_file = f"common/ideas/{idea.id[0:3]}_ideas.txt"
        if idea.id.startswith("generic"):
            out_file = f"common/ideas/lotr_generic.txt"

        # if output file doesn't exist, create it and add write "ideas = { }" into it
        if not os.path.isfile(out_file):
            with open(out_file, "w", encoding="utf-8") as f:
                f.write("ideas = {\n\t#$REMOVE$}\n")

        if out_file not in handled_files: handled_files.append(out_file)

        out_data = ParseListFromFile_asPObj(out_file)
        if out_data.Get("ideas").HasNot(cat.id):
            out_data.Get("ideas").Insert(cat.id + " = {\n\t#$REMOVE$\n}\n")
        out_data.Get("ideas").Get(cat.id).value.append(idea)

        SaveListToFile(out_data.value, out_file)
        
        # replace all #$REMOVE$ with nothing
        with open(out_file, "r", encoding="utf-8") as f:
            filedata = f.read()
            filedata = filedata.replace("#$REMOVE$", "")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(filedata)

for file in handled_files:
    reformat_code(file)
    reformat_braces(file)