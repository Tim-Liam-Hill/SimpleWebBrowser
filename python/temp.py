
#it is gross, I don't care
def get_attributes2(text):

    in_quote = False 
    in_tag = True 
    tag = "" 
    val = ""
    attributes = {}
    for c in text:
        if in_tag:
            if c == " ":
                attributes[tag] = ""
                tag = ""
            elif c == "=":
                in_tag=False
            else:
                tag += c 
        else: 
            if c == "\"":
                if in_quote:
                    attributes[tag] = val 
                    tag = ""
                    val = ""
                    in_quote = False
                    in_tag=True
                else:
                    in_quote = True 
            elif c == " ":
                attributes[tag] = val 
                tag = ""
                val = ""
                in_quote = False
                in_tag=True
            else: 
                val += c 
    return attributes
                
def get_attributes(text):
    text = text.lstrip()
    in_key = True 
    key = ""
    val = ""
    attributes = {}
    i = 0
    while i < len(text):
        if in_key: 
            if text[i] == "=":
                in_key = False
            elif text[i] == " ":
                attributes[key] = ""
                key = ""
            else:
                key += text[i]
            i += 1
        else:
            stop = " "
            if text[i] == "\"":
                stop = "\""
                i += 1
            while i < len(text) and text[i] != stop:
                val += text[i] 
                i+= 1 
            i += 1
            attributes[key] = val 
            key = "" 
            val = ""
            in_key = True 
    attributes[key] = val
            

    return attributes



tests = ['name="beans" age=10',"massive tiddies","x=\"{1:3, 24:1}\"",
    ' excalibar=mr angels mrMeow going=balistic now']

for t in tests:
    print(t, " " , get_attributes(t))


#different algorithm:
"""
1. strip start and end spaces 
2. get chars 
3. if you hit a space then add tag with empty string val 
4.if equals:
5.1 check if in quotes. If we are, go until quote 
5.2 if no quote, go until space 
"""

