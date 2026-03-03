

from pdx_parser import *



FOCUS_FILE = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\dolguldur.txt'


for f in ParseListFromFile_asPObj(FOCUS_FILE).Get("focus_tree").GetAll("focus").value:
    print('"' + f.Get("id").value + '",')