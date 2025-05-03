import module
import re,time,json, pathlib,sys, traceback,random
from datetime import datetime
from pathlib import Path
from urllib import request

FILTER="deq03_b286_0445_0867"
date="250430"
test=True

if FILTER!="":
    FILTERname="_"+FILTER
else:
    FILTERname=FILTER
input_filename_path=Path(pathlib.Path.cwd() /"make_bookmarks"/ "output_json" / "bookmark_pages.json")
output_filename="%s%s_emails"%(date,FILTERname)


class Q: # initial parameters

    path="make_bookmarks/output_pdfs/"
    #path="~/Desktop/deq02/"
    ip_filename=Path(pathlib.Path.cwd()/"log"/str("log"+(datetime.now()).strftime("%m%d%H%M%S")+".json"))
    print("Saving to: "+str(ip_filename.stem))
    people_json = json.load(open("make_database/base_people.json", 'r'))

    save=True # True (save progress if interrupted) or False (dont save progress)
    prt=False # print progress of header and email body generation
    online=False# are files local or online?
    update_people=True # update people.json with new names

    line="\n*.*"
    url_root="https://fwcpublicarchive.lib.uiowa.edu/text/"
    
    all_bookmark_pages = json.load(open(input_filename_path, 'r'))
    bookmark_pages={}
    for bm_name in all_bookmark_pages:
        if FILTER.lower() in bm_name:
            bookmark_pages.update({bm_name.lower():all_bookmark_pages[bm_name]})

######


def get_emails(FILTER,bookmark_pages=Q.bookmark_pages,people_json=Q.people_json,url_root=Q.url_root,prt=Q.prt,path=Q.path,online=Q.online):
    a=0
    i=0
    error=[]
    bms_complete=[]
    bms_notcomplete=[]
    not_completed_pages=[]
    emails_json={}

    for bm_name in bookmark_pages:
        try:
            # STEP 1: EXTRACT TEXT OF BOOKMARK
            bm_pages_text=[]
            for page_name in bookmark_pages[bm_name]:
                print("\t\t\t",page_name,"\t",end='\r')
                try:
                    if page_name[-4:] in [".txt",".pdf"]:
                        page_name=output_filename[:-4]
                    if online==True:
                        page_name= re.sub("dhhs","DHHS",page_name) #########
                        page_url=url_root+page_name+".txt"
                        response = request.urlopen(page_url)
                        page_text = response.read().decode('utf8')
                    elif online==False:
                        #print(path+"textfiles/"+page_name+".txt")
                        page_text = (open(path+"txt_pages/"+page_name+".txt","r")).read()
                    bm_pages_text.append(page_text)
                    bm_pages_text.append("\nxxxEND_PAGE:%s"%page_name)
                except Exception as e:
                    print("\t\t", str(path+"textfiles/"+page_name+".txt")," ---FILE NOT FOUND? *** *** ***")
                    print("\t\t",e,traceback.format_exc(),'\n')
                    not_completed_pages.append(page_name)
            bm_pages_text.append("\nxxxEND_BOOKMARK:%s"%bm_name)
            bm_text='\n'.join(bm_pages_text) # full text of bookmark

            # STEP 2: GET ALL HEADERS OF BOOKMARK
            try:
                headers,inc=module.getHeaders(bm_text,bm_name,prt)
                #print("----------",headers)
            except Exception as e:
                print("\t\t", bm_name, " --HEADERS NOT OBTAINED *** ***")
                print("\t\t",e,traceback.format_exc(),'\n')
                bms_notcomplete.append(bm_name)
                continue #FAILED TO GET HEADERS FOR THIS BM. CONTINUE TO NEXT

            emails={}
            i=i+1
            for header in headers:
                if len(headers) > 10:
                    print(headers.index(header)," / ",len(headers),end='\r')

                if header["metadata_order"]!=None:
                    # STEP 3: GET BODY TEXT OF BOOKMARK
                    #try:
                    email_text,body_text,last_page=module.getBody(bm_text,header,45,prt)
                    #except:
                     #   print("\t\t", bm_name, "\n",header," --HEADER BODY NOT OBTAINED *** ***")
                      #  print("\t\t",e,traceback.format_exc(),'\n')
                       # bms_notcomplete.append(bm_name)
                        #email_text="BODYERROR"
                        #body_text="BODYERROR"
                        #last_page="PAGEERROR"

                    
                    email={}
                    email["text_full"]=email_text
                    email["text_body"]=body_text
                    email["text_header"]=header["header_text"]

                    # STEP 4: GET METADATA OF BODY
                    email["sender"]=module.getSenders('\n'+email["text_header"]+'\n',people_json)
                    email["recipients_to"]=module.getTos(email["text_header"],people_json)
                    email["subject"]=module.getSubjects(email["text_header"])
                    email["attachments"]=module.getAttachments(email["text_full"])
                    email["recipients_cc"]=module.getCcs(email["text_header"],people_json)
                    email["timestamp"]=module.getTS(email["text_header"],On=True,boo=False,Unix=True,Round=-2)
                    
                    for field in email:
                        if type(email[field]) == list and field!="pages":
                            try:
                                email[field]=email[field][0]
                            except:
                                print("\n- * - * - EMPTY %s FIELD IN %s\n"%(field,bm_name))
                                if field=="timestamp":
                                    email["timestamp"]=0

                    # STEP 5: ADD DESCRIPTIVES

                    email["email_n_in_bm"]=header["metadata_order"]
                    pages= re.findall(r"xxxEND_PAGE:([A-Za-z0-9]+_b[0-9]+_[0-9]+_[0-9]+_[0-9]+).txt",email_text)
                    if pages==[]:
                        email["pages"]=[last_page.lower()] # if email does not span multiple pages
                    elif pages!=[]:
                        if "xxxEND_PAGE:" not in email_text[-13:]: # email split btwn pages, add next page
                            last_page_num=str(int( re.findall(r"_([0-9]+)$",pages[-1])[0])+1)
                            last_page=str(header["bookmark"]+"_"+last_page_num)
                            pages.append(last_page)
                        email["pages"]=[page.lower() for page in pages]
                    email["bookmark"]=header["bookmark"]
                    email["pdf"]= re.findall(r"([A-Za-z0-9]+)_b[0-9]+",header["bookmark"])[0]
                    email["department"]= re.findall(r"([A-Za-z]+)[0-9]*_b",header["bookmark"])[0]
                    email["bookmark_title"]= None#module.getTitle(header["bookmark"],Path(pathlib.Path.cwd()/"make_bookmarks"/"output_json"/"bookmark_titles.json"))
                    email["on_true"]=module.booOn(email_text)

                    # MAKE KEY
                    a=a+1
                    #key=a#module.z0s(num_emails,a)  
                    emails.update({a:email})

                    #Make/Update people file
                    if Q.update_people==True:
                        names=[email["sender"]]
                        if email["recipients_to"] not in [False,None]:
                            names.extend(list(email["recipients_to"]))
                        if email["recipients_cc"] not in [False,None]:
                            names.extend(list(email["recipients_cc"]))
                        for name in [name for name in names if type(name)==str]:
                            Found=False
                            for id in people_json:
                                try:
                                    for match in people_json[id]["matches"]:
                                        if re.findall(match,name)!=[]:
                                            Found=True
                                            people_json[id]["metadata_frequency"]+=1
                                except:
                                    #print("- * - * - Name matching failed\t",match,name)
                                    pass
                            if Found==False:
                                try:
                                    id=module.z0s(len(people_json.keys()),len(people_json.keys())+1)
                                    p={
                                        "first": re.findall(r"^([\w\W]+)\s",name)[0],
                                        "last": re.findall(r"\s([\w\W]+)$",name)[0],
                                        "matches":[name],
                                        "metadata_frequency":1                               
                                    }
                                    people_json.update({id:p})
                                except:
                                    #print(name)
                                    pass

                else: # emails missing field(s)
                    newhe=(header["bookmark"],header["header_text"])
                    error.append(newhe)

            #Save complete bookmark
                emails_json.update(emails)
                f=open(Q.ip_filename,"w")
                f.write(json.dumps(emails_json, indent = 4))
            


                p_obj = json.dumps(people_json, indent=4)
                people_filename=Path(pathlib.Path.cwd()/"make_database"/"test_output"/("%s%s_people.json"%(date,FILTERname)))
                f=open(people_filename,"w")
                f.write(p_obj)
                f.close()


        except Exception as e:
            print("- * - * - ", bm_name," --BOOKMARK NOT COMPLETED *** ***")
            print("\t\t",e,traceback.format_exc(),'\n')
            bms_notcomplete.append(bm_name)
        bms_complete.append(bm_name)            

        print('\t\t',len(bookmark_pages)-len(bms_complete),'\t',end='\r')
    
    num_emails=len(emails_json.keys())
    print(num_emails,"emails")
    new_emails_json={}
    for key in emails_json:
        key0=module.z0s(num_emails,key) # adds zeros to keys
        new_emails_json.update({key0:emails_json[key]})

    #filename=Path(pathlib.Path.cwd()/"make_database"/"test_output"/("not_completed_%s_%s.txt"%(date,FILTER)))
    #f=open(filename,"w")
    #f.write("\n".join(not_completed_pages))
    
    return new_emails_json
    

def tag_duplicates(emails_json):
    print("\nGenerating list of email pairs that are probable duplicates...") #based on timestamp-sender (t_s)
    tagged=0
    matches={}
    m_unk={}
    tagged=0
    for id in emails_json:
        t_s=str(str(emails_json[id]["timestamp"])+" "+str(emails_json[id]["sender"]))
        # Default is timestamp-sender pairs, but can add fields if want more specificity and less sensitivity

        if emails_json[id]["timestamp"] == 0 or type(emails_json[id]["sender"])!=str: # Exclude unknown fields
            m_unk[t_s]=[id]
            emails_json[id]["duplicates"]=[]
            emails_json[id]["canonical"]=True
            tagged+=1

        else:
            try:
                if t_s not in matches.keys():
                    matches.update({t_s:[id]})
                    
                else:
                    matches[t_s].append(id)
            except:
                print(id)
        #print(len(emails_json)-(list(emails_json.keys()).index(id)+1),"\t",end='\r')

    print("\n\tNumber of emails w. unique timestamp-sender: ",len(matches.keys()))
    print("\tNumber of emails w. unknown timestamp or sender: ",len(m_unk.keys()))

    p=0
    n=0
    for t_s in matches:
        if len(matches[t_s])>1:
            p=p+1
        if len(matches[t_s])==1:
            n=n+1
    print("\n\tNumber of email duplicate sets: ",p)
    print("\tNumber of email non-duplicates: ",n)

    print("\nSelecting canonical duplicates...")
    def pick_canonical(ids,emails_json):
        scored_ids=[]          
        for id in ids:
            scores=[]
            #1: num_unknowns
            num_nulls=[]
            for id_duplicate in ids:
                fields_null=len([(field,emails_json[id_duplicate][field]) for field in emails_json[id_duplicate] if emails_json[id_duplicate][field] in [None,0,[None]]])
                num_nulls.append(fields_null)
            highest=sorted(num_nulls)[-1]
            if highest>0:
                fields_null=len([(field,emails_json[id_duplicate][field]) for field in emails_json[id_duplicate] if emails_json[id_duplicate][field] in [None,0,[None]]])
                score1=0-(fields_null/highest)
            else:
                score1=0
            scores.append(score1)
            
            #2: bookmark_length
            duplicate_bookmark_lengths=[]
            for id_duplicate in ids:
                num1=int( re.findall(r"_([0-9]+)$",emails_json[id]["bookmark"])[0])
                num2=int( re.findall(r"_([0-9]+)_",emails_json[id]["bookmark"])[0])
                bookmark_num_pages=num1-num2+1
                duplicate_bookmark_lengths.append(bookmark_num_pages)
            highest=sorted(duplicate_bookmark_lengths)[-1]
            num1=int( re.findall(r"_([0-9]+)$",emails_json[id]["bookmark"])[0])
            num2=int( re.findall(r"_([0-9]+)_",emails_json[id]["bookmark"])[0])
            bookmark_num_pages=num1-num2+1
            score2=0-(bookmark_num_pages/highest)
            #print(id,"     ",emails_json[id]["duplicate_in_shortest_bookmark"],"\r")
            scores.append(score2)

            final_score=sum(scores)
            scored_ids.append((final_score,id))
        
        canon_id=sorted(scored_ids)[-1][1] #pick id with highest
        return canon_id

    coded_ids={}
    n=0
    for t_s in matches:

        ids=matches[t_s]

        if len(ids)==1: # 2 = non-duplicate, canon
            Bcode=2
            coded_ids.update({id:Bcode})
            emails_json[ids[0]]["duplicates"]=[]
            emails_json[ids[0]]["canonical"]=True
            tagged+=1
            n=n+1

        elif len(ids)>1:
            canon_id=pick_canonical(ids,emails_json)
            for id in ids:

                if id==canon_id: # 1 = duplicate, canon
                    Bcode=1 
                    coded_ids.update({id:Bcode})
                    emails_json[id]["duplicates"]=[x for x in ids if x!=id]
                    emails_json[id]["canonical"]=True
                    tagged+=1
                    n=n+1

                else: # 0 = has duplicate, non-canon
                    Bcode=0
                    coded_ids.update({id:Bcode})
                    emails_json[id]["duplicates"]=[x for x in ids if x!=id]
                    emails_json[id]["canonical"]=False
                    tagged+=1
                    n=n+1

        else:
            print(t_s,ids)
            #raise KeyboardInterrupt
        
    #print(len(emails_json)-tagged,"\t",end='\r')
    
    print('\nTagged:',tagged)
    return matches,emails_json

print("\nNum bookmarks:",len(Q.bookmark_pages.keys()))

print("\nGetting emails...")
emails_json=get_emails(FILTER)

#emails_json=json.load(open(test_output_filename, 'r'))

print("Identifying duplicates...")
matches,emails_json=tag_duplicates(emails_json)

f=open(Path(pathlib.Path.cwd()/"make_database"/"test_output" /("%s.%s"%(output_filename,"json"))),"w")
f.write(json.dumps(emails_json, indent=4))
f.close()
print("\nFinal .json saved to %s.%s"%(output_filename,"json"))

f=open(Path(pathlib.Path.cwd()/"log"/("matches_%s_%s.json"%(date,FILTER))),"w")
f.write(json.dumps(matches, indent=4))
f.close()

def clean_sql(text): #ß = '  ∆ = , ∂ = \n
    text= re.sub(r"'","ß",text)
    text= re.sub(r",","∆",text)
    text= re.sub(r"\n","∂",text)
    return text

split="', '"
emails_sql="""
CREATE TABLE `emails` (
  `id` int(11) NOT NULL,
  `text_full` longtext DEFAULT NULL,
  `text_body` longtext DEFAULT NULL,
  `text_header` longtext DEFAULT NULL,
  `sender` tinytext DEFAULT NULL,
  `recipient_to` longtext DEFAULT NULL,
  `subject` text DEFAULT NULL,
  `attachments` tinytext DEFAULT NULL,
  `recipient_cc` text DEFAULT NULL,
  `timestamp` bigint(20) DEFAULT NULL,
  `email_n_in_bm` int(11) DEFAULT NULL,
  `pages` text DEFAULT NULL,
  `bookmark` text DEFAULT NULL,
  `pdf` text DEFAULT NULL,
  `department` text DEFAULT NULL,
  `bookmark_title` text DEFAULT NULL,
  `on_true` tinyint(4) DEFAULT NULL,
  `duplicates` text DEFAULT NULL,
  `canonical` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `emails`
--

INSERT INTO `emails` (`text_full`, `text_body`, `text_header`, `sender`, `recipients_to`, `subject`, `attachments`, `recipients_cc`, `timestamp`, `email_n_in_bm`, `pages`, `bookmark`, `pdf`, `department`, `bookmark_title`, `on_true`, `duplicates`, `canonical`) VALUES
"""
for id in emails_json:
    line="\n('"
    line=line+(str(id+"', "))
    for field in emails_json[id]:
        line=line+"'"
        if type(emails_json[id][field]) in [list,tuple]:
            item='; '.join([str(p) for p in emails_json[id][field]])
        elif emails_json[id][field]==None:
            item="null"
        elif emails_json[id][field]==False:
            item="false"
        elif emails_json[id][field]==True:
            item="true"
        elif type(emails_json[id][field])==str:
            item=emails_json[id][field]
        elif type(emails_json[id][field])==int:
            item=str(emails_json[id][field])
        item=clean_sql(item)
        line=line+item
        line=line+"', "
    line=line[:-2]+")"
    emails_sql=emails_sql+line

f=open(Path(pathlib.Path.cwd()/"make_database"/"test_output" /("%s.%s"%(output_filename,".sql"))),"w")
f.write(emails_sql)
f.close()
print("\nFinal .sql saved to %s.%s"%(output_filename,"sql"))

descs={
    "num_emails_total":len(list(emails_json.keys())),
    "num_emails_withdup":0,
    "num_emails_canon":0,
    "num_emails_onsender":0,
    "num_senders_null":0,
    "num_timestamps_null":0
}

for id in emails_json:
    if emails_json[id]["duplicates"]!=[]:
        descs["num_emails_withdup"]+=1
    if emails_json[id]["canonical"]!=True: 
        descs["num_emails_canon"]+=1
    if emails_json[id]["on_true"]==True: 
        descs["num_emails_onsender"]+=1
    if emails_json[id]["sender"]==None:
        descs["num_senders_null"]+=1
    if emails_json[id]["timestamp"]==None: 
        descs["num_timestamps_null"]+=1
    if emails_json[id]["timestamp"]==0: 
        descs["num_timestamps_null"]+=1

d_text="DESCRIPTIVES for %s\n- - -\n\n"%output_filename
for item in list(descs.keys()):
    line=str(item+"\t\t\t"+str(descs[item]))+'\n'
    d_text=d_text+line

print(d_text)
f=open("make_database/test_output/descriptives_%s.json"%output_filename,"w")
f.write(d_text)
f.close()