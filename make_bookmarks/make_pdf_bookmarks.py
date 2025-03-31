import os, re, sys, PyPDF2, pathlib
from pathlib import Path
import os, re, sys, json, requests,PyPDF2, datetime,pathlib,reportlab
from datetime import datetime

def z0s(totalnum,subnum): # eg 4128, 34 .. will return 0034
    places=len(str(totalnum))
    zeros_subnum=(places-len(str(subnum)))*'0'+str(subnum)
    return zeros_subnum

def log(string):
    if os.path.isdir('log') == False:
        os.mkdir('log')
    day=str(int((datetime.timestamp(datetime.now())-1672552800)/(24*60*60)))
    filename=str("log/log"+day+".txt")
    f=open(filename,"a+")
    f.write(str((datetime.now())))
    f.write(str("\n"+string+"\n"))
    f.close()

def get_splits(outline):
    splits=[]
    for obj in outline:
        if type(obj)==PyPDF2.generic.Destination:
            split=pdf.get_destination_page_number(obj)+1
            splits.append(split)
        elif type(obj)==list:
            sub_splits=get_splits(obj)
            if type(sub_splits)==list:
                #print(sub_splits)
                sub_sub_splits=get_splits(sub_splits)
                splits.extend(sub_sub_splits)
            splits.extend(sub_splits)
    print(len(list(dict.fromkeys(splits))),"  bookmarks")
    splits=[split for split in sorted(list(dict.fromkeys(splits))) if split != 0]
    return splits

def split_pdf(pdf_path,splits,out_folder):
    #print(pdf_path,splits)
    read_input_pdf = PyPDF2.PdfReader(pdf_path)
    if splits==[]:
        pdf_writer = PyPDF2.PdfWriter()
        print(pdf_path.stem,"has no bookmarks")
        # name the bookmark
        root=re.findall("[OCR]*_*([A-Za-z]+[0-9]*)[.]",str(pdf_path))[0]
        
        zbm="1"
        zn0=z0s(len(read_input_pdf.pages),1)
        zn1=z0s(len(read_input_pdf.pages),len(read_input_pdf.pages)-1)
        bookmark_name=root+"_b"+zbm+"_"+zn0+"_"+zn1+".pdf"
        
        # write to new bookmark pdf file
        with open(Path(pathlib.Path.cwd() / "make_bookmarks" / "data" / out_folder / bookmark_name), 'wb') as out:
            pdf_writer.write(out)


    else:
        if splits[0]!=1:
            splits.insert(0,1)
        for n in splits:
            pdf_writer = PyPDF2.PdfWriter()
            # get start and end. n0 is split, n1 is a page before the next split            
            n0 = int(n)-1
            try:
                n1 = splits[splits.index(int(n))+1]-2
            except:
                n1 = len(read_input_pdf.pages)-1
                
            # get full list of page numbers in a given bookmark, eg if n0=3 & n1=6... k in [3,4,5,6]
            for k in range(n0,n1+1):
                try:
                    page = read_input_pdf.pages[k]
                    pdf_writer.add_page(page)

                except:
                    print(k,n0,n1)
                
        
            # name the bookmark
            root=re.findall("[OCR]*_*([A-Za-z]+[0-9]*)[.]",str(pdf_path))[0]
            bm_number=str(splits.index(n)+1)
            
            zbm=z0s(len(splits),bm_number)
            zn0=z0s(len(read_input_pdf.pages),n0+1)
            zn1=z0s(len(read_input_pdf.pages),n1+1)
            bookmark_name=root+"_b"+zbm+"_"+zn0+"_"+zn1+".pdf"
            
            # write to new bookmark pdf file
            with open(Path(pathlib.Path.cwd() / "make_bookmarks" / "output_pdfs" /out_folder / bookmark_name), 'wb') as out:
                pdf_writer.write(out)

input_folder="input_pdfs"
output_folder="pdf_bookmarks"

path_to_input=Path(pathlib.Path.cwd() / "make_bookmarks" / input_folder)
pdfs_list=[Path(pathlib.Path.cwd() / "make_bookmarks" / input_folder / pdf) for pdf in os.listdir(path_to_input)]
print(pdfs_list)
f=open(Path(pathlib.Path.cwd() / "make_bookmarks" / "output_json" /"bookmark_names.json"),"w")
f.write(json.dumps([str(pdf) for pdf in pdfs_list], indent = 4))

for pdf_path in sorted(pdfs_list):
    if str(pdf_path)[-4:]==".pdf":
        
        print("Splitting into bookmarks: ",pdf_path.stem)
        try:
            f = open(pdf_path,'rb')
            pdf = PyPDF2.PdfReader(f)
            outline=pdf.outline
            split_pdf(pdf_path,get_splits(outline),output_folder)
        #except Exception as e:
        #    log(str("ERROR: "+str(pdf_path)))
        #    log(str(e))
        #    print(e,pdf_path)
        #    #raise e
        except KeyboardInterrupt:
            break
        log(str(pdf_path.stem+" splitting complete."))

print("Files uploaded to dir: ",output_folder)