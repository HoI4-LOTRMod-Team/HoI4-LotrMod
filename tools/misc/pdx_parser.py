
import sys


sys.setrecursionlimit(5000) # increase if needed

tabspace = "\t"


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
            if(len(val_str) < 1): val_str = " "
            return f"{self.pre}{self.id} {self.operator} "+"{"+f"{val_str}"+"}"+f"{self.post}"
        return f"{self.pre}{self.id} {self.operator} {self.value}{self.post}"
    
    def Get(self, key):
        for obj in self.value:
            if obj.id == key:
                return obj
        return None
    
    def GetByField(self, key, value):
        for obj in self.value:
            if obj.Has(key) and obj.GetVal(key) == value:
                return obj
        return None
    
    def GetVal(self, key):
        return self.Get(key).value
    
    def Has(self, key):
        for obj in self.value:
            if isinstance(obj, PObj) and obj.id == key:
                return True
        return False
    
    def HasFieldAs(self, key, value):
        return self.Has(key) and self.Get(key).value == value
    
    def HasFieldNotAs(self, key, value):
        return self.Has(key) and self.Get(key).value != value
    
    def HasNot(self, key):
        return not self.Has(key)
    
    def WithField(self, key):
        return self.Where(lambda x: x.Has(key))
    
    def WithoutField(self, key):
        return self.Where(lambda x: not x.Has(key))
    
    def WithFieldAs(self, key, value):
        return self.Where(lambda x: x.Get(key).value == value)
    
    def WithFieldNotAs(self, key, value):
        return self.Where(lambda x: x.Get(key).value != value)
    
    def GetAll(self, key):
        return self.Where(lambda x: x.id == key)
    
    def Where(self, condition):
        ret = VirtualPObj(self)
        ret.value = [obj for obj in self.value if condition(obj)]
        return ret
    
    def First(self, condition=None):
        if condition is None:
            return self.value[0]
        return self.Where(condition).First()
    
    def Last(self, condition=None):
        if condition is None:
            return self.value[len(self.value)-1]
        return self.Where(condition).Last()
    
    def Recurse(self, NextFunction:lambda x: x, ActionFunction:lambda x: None):
        ActionFunction(self)
        next = NextFunction(self)
        if next is not None:
            next.Recurse(NextFunction, ActionFunction)

    def RecurseFind(self, NextFunction:lambda x: x, ReturnCondition:lambda x: bool):
        if(ReturnCondition(self)):
            return self
        return NextFunction(self).RecurseFind(NextFunction, ReturnCondition)
    
    def InsertAfter(self, line):
        self.parent.InsertAt(line, self.parent.value.index(self)+1)
        return self
    
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
            ret.value = block # NOTE: We do not handle list of traits/states etc. THey just get jammed in here as a string

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


def ParseObjFromFile(input_file):
    with open(input_file, 'r') as file:
        content = file.read()

        (obj, _) = Parse_PObj(content, 0)
        return obj
    

def ParseListFromFile(input_file):
    with open(input_file, 'r') as file:
        content = file.read()

        return Parse_List(content, 0)
    
def SaveObjToFile(obj, output_file):
    with open(output_file, 'w') as file:
        file.write(str(obj))

def SaveListToFile(lst, output_file):
    with open(output_file, 'w') as file:
        file.write("\n".join([str(x) for x in lst]))
    






