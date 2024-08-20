import re


class PObj:
    def __init__(self, raw:str, identifier:str, operator:str, content:str, div1:str, div2:str, div3:str):
        self.raw = raw
        self.identifier = identifier
        self.operator = operator
        self.content = content
        self.div1 = div1
        self.div2 = div2
        self.div3 = div3

    def __repr__(self):
        return (f"PObj(raw={self.raw!r}, identifier={self.identifier!r}, operator={self.operator!r}, "
                f"content={self.content!r}, div1={self.div1!r}, div2={self.div2!r}, div3={self.div3!r})")

    def __str__(self):
        return f"{self.identifier}{self.div1}{self.operator}{self.div2}{self.content}{self.div3}"

    def AsList(self):
        return PObjListFromPObj(self)



class PObjList(PObj):

    def __init__(self, raw:str, identifier:str, operator:str, content:str, div1:str, div2:str, div3:str):
        self.raw = raw
        self.identifier = identifier
        self.operator = operator
        self.content = content
        self.div1 = div1
        self.div2 = div2
        self.div3 = div3
        self.obj_list = []




def Parse_PObj(raw):
    pattern = r"""
    (?P<identifier>[a-zA-Z0-9_]+)       # Alphanumeric identifier with underscores
    (?P<div1>\s*)                       # Capture whitespace between identifier and operator
    (?P<operator>[=<>])                 # Either '=', '<' or '>'
    (?P<div2>\s*)                       # Capture whitespace between operator and content
    (?P<content>                        # Content group
        [^\s{]+                         # Content that ends with the next whitespace or newline
        |                               # OR
        \{                              # Opening curly brace
        (?:                             # Non-capturing group for nested braces
            [^{}]*                      # Any character except curly braces
            (?:                         # Non-capturing group for nested braces
                \{                      # Opening curly brace
                [^{}]*                  # Any character except curly braces
                \}                      # Closing curly brace
            )*                          # Zero or more nested braces
        )*                              # Zero or more nested braces
        \}                              # Closing curly brace
    )
    (?P<div3>\s*|\n*)                   # Capture trailing whitespaces or newlines
    """
    regex = re.compile(pattern, re.VERBOSE)
    match = regex.search(raw)
    
    return PObj(
            raw,
            match.group('identifier'),
            match.group('operator'),
            match.group('content'),
            match.group('div1'),
            match.group('div2'),
            match.group('div3')
        )


def Parse_PObjList(raw, identifier, operator, content, div1, div2, div3):
    pattern = r"""
    (?P<identifier>[a-zA-Z0-9_]+)       # Alphanumeric identifier with underscores
    (?P<div1>\s*)                       # Capture whitespace between identifier and operator
    (?P<operator>[=<>])                 # Either '=', '<' or '>'
    (?P<div2>\s*)                       # Capture whitespace between operator and content
    (?P<content>                        # Content group
        [^\s{]+                         # Content that ends with the next whitespace or newline
        |                               # OR
        \{                              # Opening curly brace
        (?:                             # Non-capturing group for nested braces
            [^{}]*                      # Any character except curly braces
            (?:                         # Non-capturing group for nested braces
                \{                      # Opening curly brace
                [^{}]*                  # Any character except curly braces
                \}                      # Closing curly brace
            )*                          # Zero or more nested braces
        )*                              # Zero or more nested braces
        \}                              # Closing curly brace
    )
    (?P<div3>\s*|\n*)                   # Capture trailing whitespaces or newlines
    """
    regex = re.compile(pattern, re.VERBOSE)
    matches = list(regex.finditer(content))

    ret = PObjList(raw, identifier, operator, content, div1, div2, div3)
    
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw = text[start:end]
        ret.obj_list.append(PObj(
            raw,
            match.group('identifier'),
            match.group('operator'),
            match.group('content'),
            match.group('div1'),
            match.group('div2'),
            match.group('div3')
        ))
    
    return ret

def PObjListFromPObj(obj:PObj):
    return Parse_PObj(obj.raw, obj.identifier, obj.operator, obj.content, obj.div1, obj.div2, obj.div3)

def Parse_RootPObjList(raw:str):
    return Parse_PObjList("", "", "", raw, "", "", "")


# Example usage
text = """
identifier1 = value1
identifier2 < {nested {block} content}
identifier3 > simple_value
"""


#q = Parse_PObj(text)
q = Parse_RootPObjList(text)
print(q)

#pobj_list = PObjList(text)
#for pobj in pobj_list.content:
    #print(pobj)
#print(str(pobj_list))  # This will print the reconstructed string of all entries joined together