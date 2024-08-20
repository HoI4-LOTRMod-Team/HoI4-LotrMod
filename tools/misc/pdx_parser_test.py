
import sys


sys.setrecursionlimit(5000) # increase if needed


class PObj:
    raw = ""

    pre = ""
    id = ""
    operator = "="
    value = ""
    post = ""

    parent = None

    level = 0

    def __str__(self) -> str:
        if(isinstance(self.value, list)):
            val_str = ''.join([str(x) for x in self.value])
            return f"{self.pre}{self.id} {self.operator} "+"{"+f"{val_str}"+"}"+f"{self.post}"
        return f"{self.pre}{self.id} {self.operator} {self.value}{self.post}"
    
    def Get(self, key):
        for obj in self.value:
            if obj.id == key:
                return obj
        return None
    
    def Contains(self, key):
        for obj in self.value:
            if obj.id == key:
                return True
        return False
    
    def Where(self, condition):
        ret = VirtualPObj(self)
        ret.value = [obj for obj in self.value if condition(obj)]
        return ret
    
    def First(self):
        return self.value[0]


class VirtualPObj(PObj):
    def __init__(self, original) -> None:
        super().__init__()
        self.raw = original.raw
        self.pre = original.pre
        self.id = original.id
        self.operator = original.operator
        self.value = original.value
        self.post = original.post
        self.parent = original.parent
        self.level = original.level



def skip_whitespace(s, i):
    j = i
    while i < len(s) and (s[i].isspace() or s[i] == "#"):
        if(s[i] == "#"):
            while i < len(s) and s[i] != "\n":
                i += 1
        i += 1
    return (s[j:i], i)

def skip_until_op_or_ws(s, i):
    j = i
    while i < len(s) and not s[i].isspace() and s[i] not in operators:
        i += 1
    return (s[j:i], i)

def skip_until_ws(s, i):
    j = i
    while i < len(s) and not s[i].isspace():
        i += 1
    return (s[j:i], i)

def skip_until_brace_closed(s, i):
    j = i
    c = 0
    while i < len(s):
        if s[i] == "{": c += 1
        if s[i] == "}":
            c -= 1
            if c == 0:
                i += 1
                break
        i += 1
    return (s[j:i], i)



operators = ["=", "<", ">"]


sample = """
focus_tree = {
	id = ered_luin
	country = {
		factor=0
		modifier = {
			add = 10
			tag = ELU
		}
	}


	default = no

	continuous_focus_position = { x = 100 y = 3000 }

	#Custom focuses start here
	focus = {
		id = thefateoferedluin
		icon = GFX_goal_a_land_of_mountains
		ai_will_do = { factor = 100 }
		x = 10
		y = 0
		mutually_exclusive = { }
		cost = 5
		available_if_capitulated = yes
		completion_reward = { add_political_power = 100 }
	}
}
"""



def Parse_PObj(text, i, parent=None):
    ret = PObj()

    j = i

    if parent:
        ret.parent = parent
        ret.level = parent.level + 1

    (ret.pre, i) = skip_whitespace(text, i)

    (ret.id, i) = skip_until_op_or_ws(text, i)

    (_, i) = skip_whitespace(text, i)

    ret.operator = text[i]
    assert ret.operator in operators
    i += 1

    (_, i) = skip_whitespace(text, i)

    if (text[i] == "{"):
        (block, i) = skip_until_brace_closed(text, i)
        ret.value = Parse_List(block[1:len(block)-1], 0, ret)
        
    else:
        (ret.value, i) = skip_until_ws(text, i)
        
    (ret.post, i) = skip_whitespace(text, i)

    ret.raw = text[j:i]

    return (ret, i)



def Parse_List(text, i, parent=None):
    ret = []

    while(i < len(text)):
        try:
            (obj, i) = Parse_PObj(text, i, parent)
            ret.append(obj)
        except:
            break

    return ret
    


(obj, _) = Parse_PObj(sample, 0)
#obj.Where(lambda x: x.id == "focus").id = "new_focus"
#print(obj)

# Select all focuses that are loose
focuses = obj.Where(lambda x: x.id == "focus")
loose_focuses = focuses.Where(lambda x: not x.Contains("relative_position_id"))

for focus in loose_focuses.value:
    preq = focus.Get("prerequisite").Get("focus").id

    preq_f = focuses.Where(lambda x: x.id == preq).First()

print(loose_focuses)


