
import pathlib
from pathlib import Path
import re,json,os

jsonfilename=Path(pathlib.Path.cwd()/"output"/"ddet1_emails_integrated.json")
dbjson = json.load(open(jsonfilename, 'r'))

def convert_names(names,att=False):

    if type(names)!=list:
        names=[names]
        List=False
    elif type(names)==list:
        List=True
    re_firstname="[A-Za-z]{3,}"
    re_lastname="[A-Z\'a-z]{2,}[- ]{0,1}[A-Za-z]+"

    names_converted=[]
    for name in names:
        try:
            if type(name)==str and att==False:
                firstname = re.findall("^"+re_lastname+"[,.][- ]("+re_firstname+")$",name)[0]
                lastname = re.findall("^("+re_lastname+")[,.][- ]"+re_firstname+"$",name)[0]
                firstlast=firstname+" "+lastname
            else:
                firstlast=str(name)
            names_converted.append(firstlast)
        except:
            names_converted.append(name)
    if List==False:
        return names_converted[0]
    elif List==True:
        return ",".join(names_converted)




filename=Path(pathlib.Path.cwd()/"output"/"ddet_emails_converted.json")
f=open(filename,"a+")

root_url="http://s-lib007.lib.uiowa.edu/flint/pdf"
for id in dbjson:
    try:
        new={
            "id":id,
            "full_text": dbjson[id]["full_text"],
            "body_text": dbjson[id]["body_text"],
            "header_text": dbjson[id]["header_text"],
            "num_in_bm": dbjson[id]["num_in_bm"],
            "pages": ",".join(dbjson[id]["pages"]),
            "bookmark": dbjson[id]["bookmark"],
            "pdf": dbjson[id]["pdf"],
            "bm_title": dbjson[id]["bm_title"],
            "on": str(dbjson[id]["On"]),
            "sender": convert_names(dbjson[id]["sender"]),
            "recipient_to": convert_names(dbjson[id]["to"]),
            "subject": dbjson[id]["subject"],
            "attachments": convert_names(dbjson[id]["attachments"],att=True),
            "recipient_cc": convert_names(dbjson[id]["Cc"]),
            "timestamp": dbjson[id]["timestamp"],
            "bookmark_url": str(root_url+"/bookmarks/"+dbjson[id]["bookmark"]+".pdf#page="+re.findall("_([0-9]+)$",dbjson[id]["pages"][0])[0]),
            "duplicates":",".join(dbjson[id]["duplicates"]),
            "dupl_canonical":str(dbjson[id]["canonical"]),
            "dupl_bm_num_pages":str(dbjson[id]["bookmark_num_pages"])
            #"dupl_in_shortest_bm":str(dbjson[id]["dupl_in_shortest_bm"])
        }
        new["num_null"]=len([(field,new[field]) for field in new if new[field] in [None,0,[None]] and field not in ["On"] and new[field]!=False])
        
        ###check
        for field in new.keys():
            if type(new[field])==int:
                new[field]=str(new[field])
            if type(new[field])==list:
                print(new[field])
                raise KeyboardInterrupt
    except:
        print(id,dbjson[id])
        raise KeyboardInterrupt

    
    f.write(json.dumps(new, indent = 4))
    f.write(",")



    






