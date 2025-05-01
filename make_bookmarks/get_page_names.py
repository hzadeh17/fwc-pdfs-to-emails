import os,sys,pathlib,json,re
from pathlib import Path

def z0s(totalnum,subnum): # eg 4128, 34 .. will return 0034
    places=len(str(totalnum))
    zeros_subnum=(places-len(str(subnum)))*'0'+str(subnum)
    return zeros_subnum

# INPUT
bms_filenames_file=Path(pathlib.Path.cwd() / "make_bookmarks" / "output_json" / "bookmark_names.json")
bm_names = [bm_name.lower() for bm_name in list(json.load(open(bms_filenames_file, 'r')))]

x={}
page_names=[]
for bm_name in bm_names:
    last_page=re.findall("[A-Za-z0-9]+_b[0-9]+_[0-9]+_([0-9]+)",bm_name)[0]
    first_page=re.findall("[A-Za-z0-9]+_b[0-9]+_([0-9]+)_[0-9]+",bm_name)[0]
    num_pages=int(last_page)-int(first_page)+1
    for i in range(1,num_pages+1):
        page_name=bm_name+"_"+z0s(num_pages,i)
        page_names.append(page_name)
        if bm_name not in list(x.keys()):
            x.update({bm_name:[page_name]})
        else:
            x[bm_name].append(page_name)

f=open(Path(pathlib.Path.cwd() / "make_bookmarks" / "output_json" /"bookmark_pages.json"),"w")
f.write(json.dumps(x, indent = 4))

f=open(Path(pathlib.Path.cwd() / "make_bookmarks" /"output_json" /"page_names.json"),"w")
f.write(json.dumps(page_names, indent = 4))
