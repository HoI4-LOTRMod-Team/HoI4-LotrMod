from pdx_parser import Parse_PObj, Parse_List, PObj, SaveListToFile, ParseListFromFile


input_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\ai_templates\lotr_templates_spiders.txt'



lst = ParseListFromFile(input_file)

#print(lst.id)

for obj in lst:
    #print(obj.id)
    for tmpl in obj.value:
        if not isinstance(tmpl, str) and tmpl.Has("stat_weights"):
            tmpl.Remove("stat_weights")
        if not isinstance(tmpl, str) and tmpl.Has("target_template"):
            tmpl.Get("target_template").Remove("match_value").Remove("weight")
        if not isinstance(tmpl, str) and tmpl.Has("allowed_types"):
            tmpl.Remove("allowed_types")
    

SaveListToFile(lst, input_file)

#print(str(lst))
