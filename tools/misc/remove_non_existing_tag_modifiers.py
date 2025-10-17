from pdx_parser import Parse_PObj, Parse_List, PObj, SaveListToFile, ParseListFromFile, ParseListFromFile_asPObj


input_file = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\doctrines\subdoctrines\land\armor_subdoctrines.txt'



lst = ParseListFromFile_asPObj(input_file)



lst.GetAllRecurse("modifier")

print(lst.GetAllRecurse("modifier"))