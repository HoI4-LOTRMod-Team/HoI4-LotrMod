from pdx_parser import Parse_PObj, Parse_List
import pyperclip


input_file = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\ered_luin.txt'



def processFocus(focus, focuses):

    children = focuses.Where(lambda x: x.Has("prerequisite") and x.Get("prerequisite").Get("focus").value == focus.GetVal("id"))

    for child in children.value:
        processFocus(child, focuses)

    if focus.HasNot("prerequisite") or focus.Has("relative_position_id"):
        return

    root_focus = focus.RecurseFind(
        lambda focus: focuses.WithFieldAs("id", focus.Get("prerequisite").Get("focus").value).First(),
        lambda x: (x.HasNot("prerequisite") or x.GetVal("id") in root_focuses) and x.HasFieldNotAs("id", focus.Get("id").value)
    )

    root_x = int(root_focus.GetVal("x"))
    root_y = int(root_focus.GetVal("y"))

    focus.Get("x").value = str(int(focus.GetVal("x")) - root_x)
    focus.Get("y").value = str(int(focus.GetVal("y")) - root_y)

    focus.GetAll("prerequisite").Last().InsertAfter("relative_position_id = "+root_focus.Get("id").value)
    



with open(input_file, 'r') as file:
    content = file.read()

    (obj, _) = Parse_PObj(content, 0)

    root_focuses = [
        "thefateoferedluin",
        "elu_warspecialists",
        "elu_athomeunderground",
        "dwarveninvestigation",
        "infrastructureeffortvalley",
        "industryeffortered",
        "restoretelcharforge",
        "reopentelcharforge",
        "homeoftheereddwarves",
        "ELU_a_change_in_course",
        "ELU_old_kingdom_not_forgotten",
        "ELU_age_of_the_miners",
        "ELU_age_of_conquest",
        "ELU_age_of_prosperity",
        "elu_agriculture_department",
        "ELU_army_defense_act",
        "ELU_reach_out_to_lindon",
        "elu_strengthenmen",
        "ELU_army_restoration_act",
        "elu_tackletheelves",
        "elu_destabilizemen",
        "elu_tacklearthedain",
        "elu_turnrhudaur",
    ]

    visited_focuses = [

    ]

    # Select all focuses that are loose
    focuses = obj.Where(lambda x: x.id == "focus")
    #loose_focuses = focuses.WithoutField("relative_position_id").WithField("prerequisite")

    focus = focuses.GetByField("id", "thefateoferedluin")
    processFocus(focus, focuses)

    pyperclip.copy(str(obj))
