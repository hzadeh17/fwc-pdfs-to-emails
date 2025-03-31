import os, re, sys, json, requests,PyPDF2, datetime,pathlib,reportlab
from datetime import datetime
from pathlib import Path
from PyPDF2 import PdfMerger
from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter
from itertools import repeat
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen.canvas import Canvas
from PIL import Image

from pdf2image import convert_from_bytes
from pdf2image import convert_from_path
import pytesseract


def log(string):
    day=str(int((datetime.timestamp(datetime.now())-1672552800)/(24*60*60)))
    filename=str("log/log"+day+".txt")
    f=open(filename,"a+")
    f.write(str((datetime.now())))
    f.write(str("\n"+string+"\n"))
    f.close()

def cleanOCRtext(text):
    import re
    text=re.sub("[^ \n]{25,}",'',text) #remove conts char strings
    return text
def enhanceImage(Image):
    # placeholder
    NewImage=Image
    return NewImage
def z0s(totalnum,subnum): # eg 4128, 34 .. will return 0034
    places=len(str(totalnum))
    zeros_subnum=(places-len(str(subnum)))*'0'+str(subnum)
    return zeros_subnum

def get_txt(pdf_pg, out_folder):
    pg_name=re.findall("/*([^/]+).pdf$",str(pdf_pg))[0]
    #create jpg
    images = convert_from_bytes(open(pdf_pg, 'rb').read())
    #path_jpg="jpgs/"+pg_name+".jpg"
    path_jpg=Path(pathlib.Path.cwd() / "make_bookmarks" / "output_pdfs" /"jpgs" / str(pg_name+".jpg"))
    images[0].save(path_jpg, 'JPEG')
        
    # OCR : textfile
    raw_text=pytesseract.image_to_string(Image.open(path_jpg))
    
    # delete .jpg
    #os.remove(page+".jpg")
    # clean OCR
    text=cleanOCRtext(raw_text)
    
    # create .txt
    f=open(Path(pathlib.Path.cwd() / "output_pdfs" / out_folder / str(pg_name+".txt")),"w")
    f.write(text)
    f.close()

if len(sys.argv)==1: #default dirs
    in_folder="pdf_pages"
    out_folder="txt_pages"
else: #manual entry
    in_folder= sys.argv[1]
    out_folder=sys.argv[2]

replace=False
files_online=False

if files_online==False:
    path_to_folder=Path(pathlib.Path.cwd() / "make_bookmarks" / "output_pdfs" / in_folder)
    pdfs_list=[Path(pathlib.Path.cwd() / "make_bookmarks" / "output_pdfs" / in_folder / pdf) for pdf in os.listdir(path_to_folder)]
elif files_online==True:
    path_to_names=Path(pathlib.Path.cwd() / "make_bookmarks" / "output" / "page_names.json"),
    pdfs_list=list(json.load(open(path_to_names, 'r')))

for pdf_path in sorted(pdfs_list):
    try:
        if replace==False and str(pdf_path.stem+".txt") in os.listdir(Path(pathlib.Path.cwd() / "make_bookmarks" / "output_pdfs" / out_folder)):
            print("text already exists: ", pdf_path.stem)
            continue
        else:
            print("OCR-ing page: ",pdf_path.stem)
            get_txt(pdf_path, Path(pathlib.Path.cwd() / "make_bookmarks" / "output_pdfs" / out_folder))
    except KeyboardInterrupt:
        log(str("Stopped   "+str(pdf_path)))
        break
    #except Exception as e:
     #   log(str("ERROR:"+str(pdf_path)))
      #  log(str(e))
