

from pdx_parser import *
from locfile import LocFile


FOCUS_FILE = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\gundabad.txt'


loc_file = LocFile(r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\localisation\english\gundabad\gundabad_focus_l_english.yml')

for f in ParseListFromFile_asPObj(FOCUS_FILE).Get("focus_tree").GetAll("focus").value:
#for f in ParseListFromFile_asPObj(FOCUS_FILE).GetAll("joint_focus").value:
    print('("' + f.Get("id").value + '", ' + '"' + loc_file.get(f.Get("id").value) + '"),')