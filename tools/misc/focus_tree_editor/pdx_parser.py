
import sys


sys.setrecursionlimit(5000) # increase if needed

tabspace = "\t"


class PLooseToken:
    raw = ""

    pre = ""
    id = ""
    value = ""
    post = ""

    parent = None

    level = 0

    def __str__(self) -> str:
        return f"{self.pre}{self.value}{self.post}"


class PObj:
    raw = ""

    pre = ""
    id = ""
    operator = "="
    value = ""
    post = ""

    parent = None

    level = 0

    # Is the value of this obj a list or a single string?
    def ValueIsList(self) -> bool:
        return isinstance(self.value, list)

    def __str__(self) -> str:
        if(isinstance(self.value, list)):
            val_str = ''.join([str(x) for x in self.value])
            if(len(val_str) < 1): val_str = " "
            return f"{self.pre}{self.id} {self.operator} "+"{"+f"{val_str}"+"}"+f"{self.post}"
        return f"{self.pre}{self.id} {self.operator} {self.value}{self.post}"
    
    # Get the value of this obj as a string (regardless of list or not)
    def GetValueString(self, withBrackets=True):
        if(isinstance(self.value, list)):
            val_str = ''.join([str(x) for x in self.value])
            if(len(val_str) < 1): val_str = " "
            if withBrackets:
                return "{"+f"{val_str}"+"}"
            else:
                return f"{val_str}"
        return f"{self.value}"
    
    # Get the first child object by id (example: techs.Get("light_cav_1"))
    def Get(self, key):
        for obj in self.value:
            if obj.id == key:
                return obj
        return None
    
    # Get any childobjects based on a key value (example: focuses.GetByField("id", "the_fate_of_ered_luin"))
    def GetByField(self, key, value):
        for obj in self.value:
            if obj.Has(key) and obj.GetVal(key) == value:
                return obj
        return None
    
    # Get the *value* of a child object by id (equivalent to Get(key).value)
    def GetVal(self, key):
        return self.Get(key).value
    
    # Does this obj have a child with the given id?
    def Has(self, key):
        for obj in self.value:
            if isinstance(obj, PObj) and obj.id == key:
                return True
        return False
    
    # Does this obj have a child with the given id and value?
    def HasFieldAs(self, key, value):
        return self.Has(key) and self.Get(key).value == value
    
    # Does this obj have a child with given id, BUT the value is not equal to the given value
    def HasFieldNotAs(self, key, value):
        return self.Has(key) and self.Get(key).value != value
    
    # Does this object not have a child with the given id
    def HasNot(self, key):
        return not self.Has(key)
    
    # Returns a VirtualPObj clone that only has the children that meet the given condition(obj) -> true
    def Where(self, condition):
        ret = VirtualPObj(self)
        ret.value = [obj for obj in self.value if condition(obj)]
        return ret
    
    # Returns a clone that only retains the children that have the given field (example: focuses.WithField("prerequisite").WithoutField("relative_position_id"))
    def WithField(self, key):
        return self.Where(lambda x: x.Has(key))
    
    # Returns a clone that only retains the children that do not have the given field (example: focuses.WithField("prerequisite").WithoutField("relative_position_id"))
    def WithoutField(self, key):
        return self.Where(lambda x: not x.Has(key))
    
    # Returns a clone that only retains the children that have the given field with the given value (example: focuses.WithFieldAs("prerequisite", "fate_of_ered_luin"))
    def WithFieldAs(self, key, value):
        return self.Where(lambda x: x.Get(key).value == value)
    
    # Negation of WithFieldAs
    def WithFieldNotAs(self, key, value):
        return self.Where(lambda x: x.Get(key).value != value)
    
    # Get clone that only have the children with the given name
    def GetAll(self, key):
        return self.Where(lambda x: x.id == key)
    
    # Get all child and sub-child objects that have the given id
    def GetAllRecurse(self, key):
        ret = VirtualPObj(self)
        ret.value = []
        self.GetAllRecurse_helper(ret, key)
        return ret
            
    # Helper function for the method above
    def GetAllRecurse_helper(self, vpo, key):
        for obj in self.value:
            if obj.id == key:
                vpo.value.append(obj)
            if obj.ValueIsList():
                obj.GetAllRecurse_helper(vpo, key)
    
    # Get the first child object that meets the given condition
    def First(self, condition=None):
        if condition is None:
            return self.value[0]
        return self.Where(condition).First()
    
    # Get the last child object that meets the given condition
    def Last(self, condition=None):
        if condition is None:
            return self.value[len(self.value)-1]
        return self.Where(condition).Last()
    
    # ...
    def Recurse(self, NextFunction:lambda x: x, ActionFunction:lambda x: None):
        ActionFunction(self)
        next = NextFunction(self)
        if next is not None:
            next.Recurse(NextFunction, ActionFunction)

    # ...
    def RecurseFind(self, NextFunction:lambda x: x, ReturnCondition:lambda x: bool):
        if(ReturnCondition(self)):
            return self
        return NextFunction(self).RecurseFind(NextFunction, ReturnCondition)
    
    # Insert a new line of text after a certain line ?
    def InsertAfter(self, line):
        self.parent.InsertAt(line, self.parent.value.index(self)+1)
        return self
    
    # ...
    def InsertAt(self, line, index):
        if(len(self.value) < 1):
            self.Insert(line)
        else:
            (nobj, _) = Parse_PObj(line, 0, self)
            cobj = self.value[min(index, len(self.value)-1)]
            pobj = self.value[max(index-1, 0)]

            nobj.post = cobj.post
            if("\n" not in line and "\n" not in self.raw):
                pobj.post = " "
            else:
                pobj.post = "\n" + tabspace*nobj.level
            self.value.insert(index, nobj)
        return self

    # ...
    def Insert(self, line):
        if(len(self.value) > 0):
            self.InsertAt(line, len(self.value))
        else:
            (nobj, _) = Parse_PObj(line, 0, self)
            if("\n" not in line and "\n" not in self.raw):
                nobj.post = " "
            else:
                nobj.post = "\n" + tabspace*nobj.level
            self.value.append(nobj)
        return self

    # Remove a child with a certain id
    def Remove(self, key):
        if not self.Has(key):
            return self
        rm = self.Get(key)
        self.value.remove(rm)
        return self
        


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

def skip_until_literal_closed(s, i):
    j = i
    assert s[i] == '"'
    i += 1
    while i < len(s):
        if s[i] == '"':
            if s[i-1] != '\\':
                i += 1
                break
        i += 1
    return (s[j:i], i)



operators = ["=", "<", ">"]


def Parse_Token(text, i=0, parent=None):
    ret = PLooseToken()

    j = i

    if parent:
        ret.parent = parent
        ret.level = parent.level + 1

    (ret.pre, i) = skip_whitespace(text, i)

    (ret.value, i) = skip_until_ws(text, i)
    ret.id = ret.value
        
    (ret.post, i) = skip_whitespace(text, i)

    ret.raw = text[j:i]

    return ret, i


def ParseTokenList(text, i=0, parent=None):
    ret = []

    while(i < len(text)):
        try:
            (obj, i) = Parse_Token(text, i, parent)
            ret.append(obj)
        except:
            break

    return ret




def Parse_PObj(text, i=0, parent=None):
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
        if "=" in block or block[1:len(block)-1].isspace():
            ret.value = Parse_List(block[1:len(block)-1], 0, ret)
        else:
            ret.value = ParseTokenList(block[1:len(block)-1], 0, ret)

    elif (text[i] == "\""):
        (block, i) = skip_until_literal_closed(text, i)
        ret.value = block
        
    else:
        (ret.value, i) = skip_until_ws(text, i)
        
    (ret.post, i) = skip_whitespace(text, i)

    ret.raw = text[j:i]

    return ret, i



def Parse_List(text, i=0, parent=None):
    ret = []

    while(i < len(text)):
        try:
            (obj, i) = Parse_PObj(text, i, parent)
            ret.append(obj)
        except:
            break

    return ret

def Parse_List_asPObj(text, i=0, parent=None):
    lst = Parse_List(text, i, parent)

    ret = PObj()
    ret.value = lst
    return ret


def ParseObjFromFile(input_file):
    with open(input_file, 'r') as file:
        content = file.read()

        (obj, _) = Parse_PObj(content, 0)
        return obj
    

def ParseListFromFile(input_file):
    with open(input_file, 'r') as file:
        content = file.read()

        return Parse_List(content, 0)
    
def ParseListFromFile_asPObj(input_file):
    with open(input_file, 'r') as file:
        content = file.read()

        return Parse_List_asPObj(content, 0)
    
def SaveObjToFile(obj, output_file):
    with open(output_file, 'w') as file:
        file.write(str(obj))

def SaveListToFile(lst, output_file):
    with open(output_file, 'w') as file:
        file.write("\n".join([str(x) for x in lst]))
    






