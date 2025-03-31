from pathlib import Path
import os, re, sys, json, PyPDF2,pathlib
from datetime import datetime



def z0s(totalnum,subnum): # eg 4128, 34 .. will return 0034
    places=len(str(totalnum))
    zeros_subnum=(places-len(str(subnum)))*'0'+str(subnum)
    return zeros_subnum

def log(string):
    day=str(int((datetime.timestamp(datetime.now())-1672552800)/(24*60*60)))
    filename=str("log/log"+day+".txt")
    f=open(filename,"a+")
    f.write(str((datetime.now())))
    f.write(str("\n"+string+"\n"))
    f.close()

def split_bms_to_pages(bookmark_path,out_folder):
    bm_name=re.findall("/*([^/]+).pdf$",str(bookmark_path))[0]
    print("splitting into single pgs: ",bm_name)
    pagenames=[]
    pdfpagefiles=[]
    with open(bookmark_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for i in range(len(pdf_reader.pages)):
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[i])
            # Naming convention
            page_num=z0s(len(pdf_reader.pages),i+1)
            pagename=bm_name+"_"+page_num
            pagenames.append(pagename)
            output_filename = Path(pathlib.Path.cwd() / "make_bookmarks" / "output_pdfs" / out_folder / str(pagename+".pdf"))
            # Output 1-pg file
            pdfpagefiles.append(output_filename)
            with open(output_filename, 'wb') as output_file:
                pdf_writer.write(output_file)
    log(str(bm_name+" : "+ str(len(pdfpagefiles))+" pages"))

if len(sys.argv)==1: #default dirs
    in_folder="pdf_bookmarks"
    out_folder="pdf_pages"
else: #manual entry
    in_folder= sys.argv[1]
    out_folder=sys.argv[2]


path_to_folder=Path(pathlib.Path.cwd() / "make_bookmarks" / "output_pdfs" / in_folder)
pdfs_list=[Path(pathlib.Path.cwd() / "make_bookmarks" / "output_pdfs" / in_folder / pdf) for pdf in os.listdir(path_to_folder)]

for pdf_path in sorted(pdfs_list):
    #print(pdf_path.stem)
    if str(pdf_path)[-4:]==".pdf":
        try:
            split_bms_to_pages(pdf_path,out_folder)
        except KeyboardInterrupt:
            log("Stopped ",pdf_path)
            break
        except Exception as e:
            log(str("ERROR:"+str(pdf_path)))
            log(str(e))
            raise e
        log(str(pdf_path.stem+"pdf page parsing complete"))
    else:
        print(pdf_path)