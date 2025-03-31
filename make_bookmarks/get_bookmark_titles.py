
import os, re, sys, json, pathlib, datetime, urllib
from pathlib import Path
import PyPDF2

def z0s(totalnum,subnum): # eg 4128, 34 .. will return 0034
    places=len(str(totalnum))
    zeros_subnum=(places-len(str(subnum)))*'0'+str(subnum)
    return zeros_subnum

def log(string):
    #day=str(int((datetime.timestamp(datetime.now())-1672552800)/(24*60*60)))
    day="1"
    filename=str("../logs/log"+day+".txt")
    f=open(filename,"a+")
    #f.write(str((datetime.now())))
    f.write(str("\n"+string+"\n"))
    f.close()

def bookmark_dict(bookmark_list,pdf):
    result = {}
    for item in bookmark_list:
        if isinstance(item, list):
            # recursive call
            result.update(bookmark_dict(item,pdf))
        else:
            try:
                result[pdf.get_destination_page_number(item)+1] = item.title
            except:
                pass
    return result

def get_bm_titles(path,dep):
    
    f = open(path,'rb')
    pdf = PyPDF2.PdfReader(f)

    outline = pdf.outline
    num_pgs = len(pdf.pages)
    bm_dict=bookmark_dict(outline,pdf)
    
    b={}
    for start_pg in bm_dict.keys():
        bm_title=bm_dict[start_pg]
        index=list(bm_dict.keys()).index(start_pg)
        try:
            next_bm_start_pg=list(bm_dict.keys())[index+1]
        except IndexError:
            next_bm_start_pg=num_pgs
        end_pg=next_bm_start_pg-1

        # naming bookmark
        _b=z0s(len(bm_dict.keys()),str(index+1))
        p1=z0s(num_pgs,start_pg)
        p2=z0s(num_pgs,end_pg)
        bm_name=dep+"_b"+_b+"_"+p1+"_"+p2

        # getting pages
        pgs=[]
        num_pgs_in_bm=(end_pg-start_pg)+1
        for i in range(num_pgs_in_bm):
            pg=z0s(num_pgs_in_bm,i+1)
            pg_name=bm_name+"_"+pg
            pgs.append(pg_name)

        #b.update({bm_title:pgs})
        b.update({bm_title:bm_name})

    file_b={dep:b}
    return file_b

in_folder="pdfs"
out_file="bookmark_titles.json"

path_to_folder=Path(pathlib.Path.cwd() / "data" / in_folder) # put full pdfs here
pdfs_list=[Path(pathlib.Path.cwd() / "data" / in_folder / pdf) for pdf in os.listdir(path_to_folder)]

deps_titles={}
for path in pdfs_list:
    try:
        dep=re.findall("OCR_([A-Za-z]+[0-9]*)",str(path))[0].lower()
        dep_titles=get_bm_titles(path,dep)
        deps_titles.update(dep_titles)
        print(path,end='\r')
    except Exception as e:
        log(str("ERROR: "+str(path)))
        log(str(e))
        print(">>>",e,path)
        raise e
    except KeyboardInterrupt:
        break

# save
with open(Path(pathlib.Path.cwd() / ".." / "output" / out_file), 'w') as f:
    json.dump(deps_titles, f)