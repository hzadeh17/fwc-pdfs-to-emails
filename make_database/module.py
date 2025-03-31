from pathlib import Path
import pathlib
import re,json,datetime,dateutil.parser,time

# EMAIL BOUNDARY FUNCTIONS

def getHeaders(text,bm,prt=False): #Returns headers of email
    text="\n"+text
    line="\n*.*"

    # GET START METADATA (From: or On...)
    start_mds=getSenders(text,people_list={},boo=True,prt=0,On=True)
    start_mds=[start_md for start_md in start_mds if start_md!=None]
    start_mds=[start_md for start_md in start_mds if len(start_md)<200]

    #Add one line
    start_mds_line=[]
    start_mds_fin=[]
    for start_md1 in start_mds:
        start_md2=re.findall(as_regex(start_md1)+line,text)[start_mds_fin.count(start_md1)-1]
        start_mds_line.append(start_md2)
        start_mds_fin.append(start_md1)
    if len(start_mds)!=len(start_mds_line):
        print('\nProblem with start metadata in ',bm)
        print("\n>>>1\t",'\t'.join(start_mds))
        print("\n>>>2\t",'\t'.join(start_mds_line))
        raise KeyboardInterrupt

    full_metadata=[]
    incompletes=[]
    sec_per_head=0
    start_mds_complete=[]
    if start_mds_line==[]: # No starts found
        try:
            #bm_pg=re.findall("([A-Za-z0-9]+_b[0-9]+_[0-9]+_[0-9]+)_endBOOKMARK_\n*$",text)[0]
            new={
                        "bookmark":bm, 
                        "header_text":None,
                        "metadata_order":None
                    }
            full_metadata.append(new)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            print("ERROR--- ",e)

    elif start_mds_line !=[]:
        
        # CHECK FOR IDENTICAL START METADATAS, just for check at the end
        repeats_test=len(start_mds_line)-len(list(dict.fromkeys(start_mds_line)))
        repeats=[]
        if repeats_test!=0:
            for start_md in start_mds_line:
                x=0
                for start_md in start_mds_line:
                    if start_md==start_md:
                        x=x+1
                if x>1:
                    repeats.append(start_md)
            #print("\n\n--- Repeats present in %s:\n"%bm,'\n',('\n'.join(repeats)),"\n\n---\n")

        # Loop through start metadata
        for start_md in start_mds_line:
            print("\t\t\t\t",end='\r')
            print(start_mds_line.index(start_md)," / ",len(start_mds_line),end="\r")
            start_time = time.time()
            
            # IF START MD IS "On...""
            if booOn(start_md)==True: # On line
                header=re.findall("[0O]+n.*\n*.*wro.*",start_md)[0]
                p("%s\n___ 'On...' LINE FOUND; FIN!\n\n"%header,prt)
                new={
                        "bookmark":bm,
                        "header_text":header,
                        "metadata_order":start_mds_line.index(start_md)+1
                    }
                full_metadata.append(new)

            # IF START MD IS "From: ...""
            else:
                stop=False
                i=0
                checkpt_i=0
                prevnumFromMetadata=0

                header=""
                bm_end=[]
                while numFromMetadata(header) in [i for i in range(0,7)] and bm_end==[] and stop==False:
                    i=i+1
                    #print(as_regex(start_md)+(i*line))
                    header=re.findall(as_regex(start_md)+(i*line),text)[0]
                    p("\n___ ___ ___ BEGIN LOOP %i ___ ___ ___\n"%i,prt)

                    p("___LOOP %i CHECK: does adding new line add more metadata?\n"%i,prt)
                    if numFromMetadata(header)==None: # adds From -> take header, minus 2nd From line
                        p("%s\n__LOOP %i__A: Ran into new start md; rolled back; FIN!\n"%(re.findall("\n.*$",header)[0],i),prt)
                        header=re.findall(as_regex(start_md)+((checkpt_i)*line),text)[0]
                        checkpt_i=checkpt_i-1
                        stop=True
                   
                    elif numFromMetadata(header) > prevnumFromMetadata and booOn(header)==False: # adds metadata -> great, keep going
                        checkpt_i=i
                        header=re.findall(as_regex(start_md)+(i*line),text)[0]
                        prevnumFromMetadata=numFromMetadata(header)
                        try:
                            p("%s\n__LOOP %i__B: Metadata added; proceed...\n"%(re.findall("\n.*$",header)[0],i),prt)
                        except:
                            print("\n\n>>>Error:",bm,"\n",header,'\n',start_mds_line)
                            #raise KeyboardInterrupt
                        stop=False
                    
                    elif numFromMetadata(header) == prevnumFromMetadata: # does not add metadata -> check next 3 lines
                        p("%s\n__LOOP %i__C: No md added; subcheck activated...\n"%(re.findall("\n.*$",header)[0],i),prt)

                        k=4 # Number of tries
                        for a in range(1,k+1):
                            try_numFromMetadata=numFromMetadata(re.findall(as_regex(start_md)+((i+a)*line),text)[0])
                            header=re.findall(as_regex(start_md)+((i+a)*line),text)[0]
                            if try_numFromMetadata==None:
                                p("%s\n__LOOP %i__C.1: Ran into new start md; rolled back; FIN!\n"%(re.findall("\n.*$",header)[0],i),prt)
                                stop=True
                                break
                            elif try_numFromMetadata==prevnumFromMetadata: # no new metadata
                                p("%s\n__LOOP %i__C.2: No md added...%i\n"%(re.findall("\n.*$",header)[0],i,a),prt)
                                if a!=k:
                                    stop=False
                                elif a==k:
                                    stop=True
                                    pass
                                pass
                            elif try_numFromMetadata > prevnumFromMetadata: # BINGO
                                stop=False
                                prevnumFromMetadata=numFromMetadata(header)
                                checkpt_i=i+a
                                i=i+a
                                p("%s\n__LOOP %i__C.3: Metadata added; proceed...\n"%(re.findall("\n.*$",header)[0],i),prt)
                                break

                    if i<12 and stop==False:
                        p("%s\n___LOOP %i complete; Proceed...\n\n_ _ _\n"%(re.findall("\n.*$",header)[0],i),prt)
                        header=re.findall(as_regex(start_md)+((checkpt_i)*line),text)[0]
                        pass
                    elif i>=12 or stop==True:
                        p("\n___LOOP %i complete; FIN!\n\n_ _ _\n"%i,prt)
                        header=re.findall(as_regex(start_md)+((checkpt_i)*line),text)[0]

                     
                    bm_end=re.findall("_BOOKMARK_",header)
                     

                p("FIN: final # lines = %i"%checkpt_i,prt)
                header=re.findall(as_regex(start_md)+(checkpt_i*line),text)[0] # if Yes, take what we've got
                sec_per_head=int(time.time() - start_time)

                if numFromMetadata(header)!=None:
                    if numFromMetadata(header)>1:
                        #bm=re.findall("([A-Za-z0-9]+_b[0-9]+_[0-9]+_[0-9]+)_endBOOKMARK_\n*$",text)[0]
                        new={
                            "bookmark":bm, 
                            "header_text":header,
                            "metadata_order":start_mds_line.index(start_md)+1
                        }
                        full_metadata.append(new)
                    else:
                        incompletes.append(header)
            #print("Headers: ",start_mds.index(md1),"/",len(start_mds),"  ",end="\r")
            p(str("\n_ _ _ FINAL HEADER _ _ _ in %i sec\n%s\n* * * FIN! * * *\n")%(sec_per_head,header),prt)            

    return full_metadata,incompletes

def getBody(bm_text,header,time_limit,prt=False): # Returns body of email
    bm_text="\n"+bm_text
    line="\n*.*"
    start_time = time.time()
    startnum_metadata=numFromMetadata(header["header_text"])
    bm_end=[]

    p("\n___GETTING EMAIL BODY___\nnum md = %i"%startnum_metadata,prt)
    email_text=re.findall(as_regex(header["header_text"]),bm_text)[0]
    p(as_regex(header["header_text"]),prt)
    x=0
    while numFromMetadata(email_text+'\n')==startnum_metadata and len(bm_end)==0:
        if (time.time() - start_time)<time_limit:
            x=x+1
        else:
            break
        email_text=re.findall(as_regex(header["header_text"])+(x*line),bm_text)[0]
        bm_end=re.findall("xxxEND_BOOKMARK:",email_text)
        p("%s\n___New line %i added!\n"%(re.findall("\n.*$",email_text)[0],x),prt)

    if bm_end!=[]:
        p("\n___Ran into bookmark end; FIN!\n",prt)
    if numFromMetadata(email_text)!=startnum_metadata or numFromMetadata(email_text)==None:
        p("%s\n___Ran into new md; rolled back; FIN!\n"%re.findall("\n.*$",email_text)[0],prt)


    email_text=re.findall(as_regex(header["header_text"])+(x-1)*line,bm_text)[0]
    sec_per_body=int(time.time() - start_time)
    p("\n_ _ _ FINAL BODY _ _ _ in %i sec\n%s\n* * * FIN! * * *\n"%(sec_per_body,email_text),prt)

    # get body isolated
    #print(str(as_regex(header["header_text"])+"("+(x-1)*line+")"))
    body_text=re.findall(str(as_regex(header["header_text"])+"("+(x-1)*line+")"),email_text)[0]

    # get Nearest Page
    o=1
    text=email_text
    stop=False

    while 'xxxEND_PAGE:' not in text:
        try:
            reg_exp_text=re.sub("[^\w\n\s]",".",text)
            text=re.findall(reg_exp_text+(o*line),bm_text)[0]
            #text=re.findall(str(main.clean_text(text)+(o*line)),bm_text)[0]
            o=o+1
        except:
            print("Error in getBody:\n",text,"\n______\n")
            raise KeyboardInterrupt

    last_page=re.findall("xxxEND_PAGE:([A-Za-z0-9]+_b[0-9]+_[0-9]+_[0-9]+_[0-9]+)",text)[0]

    return email_text,body_text,last_page#,x,sec_per_body

def numFromMetadata(text): #Returns count of metadata fields present

    start_mds=getSenders(text,people_list={},boo=True)
    start_mds=[start_md for start_md in start_mds if start_md!=None]
    start_mds=[start_md for start_md in start_mds if len(start_md)<200]

    if len(start_mds)==1:
        if re.findall("\n+\W*[O0]+n.*wro.e[:;\s]*\n|\n+\W*[O0]+n.*\n*.*wro.e[:;\s]*\n",text)!=[]: #On
            numOn=lenif(re.findall("\n+\W*[O0]+n.*wro.e[:;\s]*\n|\n+\W*[O0]+n.*\n*.*wro.e[:;\s]*\n",text))
            return None
        else: #From        
            numTS_From=lenif(getTS(text,On=False,boo=True))
            numSen_From=lenif(getSenders(text,people_list,boo=True,prt=0,On=False))
            numTo=lenif(getTos(text,people_list,boo=True))
            numCc=lenif(getCcs(text+"\n",people_list,boo=True))
            numSub=lenif(getSubjects(text,boo=True))
            numAtt=lenif(getAttachments(text))
            return sum([numTS_From,numSen_From,numTo,numCc,numSub,numAtt])

    elif len(start_mds)==0: # if no starts
        return 0
    elif len(start_mds)>1: # if more than one start (from or on)
        return None

def getTitle(bookmark,filename): # Get embedded title of pdf bookmark
    found=False
    data = json.load(open(filename,"r"))
    for dep in data:
        if dep.lower() in bookmark.lower():
            for bm_title in data[dep]:
                data_bookmark=data[dep][bm_title]
                if data_bookmark.lower()==bookmark.lower():
                    found=True
                    return bm_title
                else:
                    pass
    if found==False:
        return None

people_list = json.load(open("make_database/output/people.json", 'r'))

# METADATA FUNCTIONS

def getSenders(text,people_list={},boo=False,prt=0,On=True):

    name_list = re.findall("\n+\W*.rom[:; \W]+.*|\n+\W*Fr[ea]m[:; \W]+.*|\n+\W*from[:; \W]+.*|\n+\W*¥romi*[:; \W]+.*|\n+\W*Fro[imntyve]*[:; \W]+.*|\n+\W*[O0]+n.*wro.e[:;\s]*\n|\n+\W*[O0]+n.*\n*.*wro.e[:;\s]*\n",text)
    if boo==True and On==True:
        return [name for name in name_list if len(name)<120]
    if boo==True and On==False:
        return [name for name in name_list if len(name)<70 and booOn(name)==False]
    elif boo==False:
        if name_list==[]:
            return None # No sender found = no email
        else:
            nonnames=[]
            Ons=[]
            Froms=[]
            final_list=[]
            for thing in name_list:
                # ONs
                ons = re.findall("[O0]n.*\n*.*wro.e[:;\n]", thing) #find ons
                if ons != []:
                    for on in ons:
                        try:
                            name=re.findall("[O0]n.*[PAM0-9]+,([^˚]+)[<]*.*wro.e[:;\n]+$",on)[0]
                            clean_on_name=fix_name(name,people_list)
                            if 5<len(clean_on_name)<27:
                                Ons.append(clean_on_name)
                                if On==True:
                                    final_list.append(clean_on_name)
                                else:
                                    Ons.append(None)
                        except:
                            print("CAN NOT READ On... FIELD: ",ons)
                            Ons.append(None)
                        
                    
                # FROMs
                froms = re.findall("\n.{0,10}[\WﬁFEKrIifY¥C][si]*r[eao][enmtyvi]+[-:;'.](.{0,70})", thing) #find froms
                if froms != []:
                    for fro in froms:
                        clean_fro_name=fix_name(fro,people_list)
                        if 5<len(clean_fro_name)<27:
                            Froms.append(clean_fro_name)
                            final_list.append(clean_fro_name)
                        else:
                            Froms.append(None)
                            final_list.append(None)
                if froms==[] and ons==[]:
                    nonnames.append(thing)
            if len(final_list)+len(nonnames)!=len(name_list) and prt==1:
                print("ERR ",len(name_list),len(final_list),len(nonnames))
            #return name_list
            return final_list

def getTos(e4,people_list={},boo=False,prt=0):
    name_list = re.findall("\n.{0,10}T[oa][:;]+.*|.*[O0]n.*wro[ft]e.|[O0]n.*\n*.*wro[tf]e[:;\n]",e4)
    if boo==True:
        return [name for name in name_list if booOn(name)==False]

    elif boo==False:
        if name_list==[]:
            return None # Not false because there should always be a recipient, if not On...
        else:
            nonnames=[]
            final_list=[]
            for thing in name_list:
                # ONs
                ons = re.findall("[O0]n.*\n*.*wro.e[:;\n]", thing) #find ons
                if ons != []:
                    final_list.append(False)
                # TOs
                else:
                    recs = re.findall("\n\W*T[oa](.*)", thing) #find tos
                    if recs != []:
                        for rec in recs:
                            recset=[]
                            recnames=re.split(";|>,|\),|\",|\',",rec)
                            for recname in recnames:
                                fixed_rec_name=fix_name(recname,people_list)
                                if 5<len(fixed_rec_name)<27:
                                    recset.append(fixed_rec_name)
                                else:
                                    recset.append(None)
                            final_list.append(tuple(recset))

                    elif recs==[]:
                        nonnames.append(thing)
                        final_list.append(None)
                    if len(final_list)+len(nonnames)!=len(name_list) and prt==1:
                        print("ERR ",len(name_list),len(final_list),len(nonnames))
            return final_list

def getCcs(e4,people_list={},boo=False,prt=0):
    #name_list = re.findall("\n.{0,10}T[oa][:;]+.*\n+.*C[ec]+[:;]+.*\n*.*\n*Subj|\n.*T[oa][:;]+.*\n+.*C[ec]+[:;]+.*\n|\n.{0,10}T[oa][:;]+.*|\n.{0,10}[O0]n.*\n*.*wro.e.",e4)
    name_list = re.findall("\n.{0,10}T[oa][:;]+.*\n+.*C[ec]+[:;]+.*\n*.*\n*Subject[:;]|\n.{0,10}T[oa][:;]+.*|\n.{0,10}[O0]n.*\n*.*wro.e.",e4)
    if boo==True:
        #return re.findall("\n+.*C[ec]+[:;]+.*\n*.*\n*.*\n*.*\n*Subj|\n.*T[oa][:;]+.*\n+.*C[ec]+[:;]+.*\n",e4)
        return re.findall("\n+.*C[ec]+[:;]+.*",e4)

    elif boo==False:
        if name_list==[]:
            return False # No Cc: line which is ok!
        else:
            nonnames=[]
            final_list=[]

            for thing in name_list:
                # ONs
                ons = re.findall("[O0]n.*\n*.*wro.e[:;\n]", thing) #find ons
                if ons != []:
                    final_list.append(False)
                # CCs
                else:
                    recs = re.findall("C[ec]+[:;]+([^˚]+)\n", thing) #find tos
                    if recs != []: # Cc line present
                        for rec in recs:
                            recset=[]
                            recnames=re.split(";|>,|\),|\",|\',",rec)
                            for recname in recnames:
                                fixed_rec_name=fix_name(recname,people_list)
                                if 5<len(fixed_rec_name)<27:
                                    recset.append(fixed_rec_name)
                                else:
                                    recset.append(None)
                            final_list.append(tuple(recset))
                    elif recs==[]: # No Cc line
                        nonnames.append(thing)
                        final_list.append(False)
                    if len(final_list)+len(nonnames)!=len(name_list) and prt==1:
                        print("ERR ",len(name_list),len(final_list),len(nonnames))
            return final_list

def getAttachments(emailstext,List=True):
    attachment_lists=[]
    line='\n*.*'
    att_lines = re.findall(str("Attachments[:;]+[\s]*("+(3*line)+"\n*)"), emailstext)

    if att_lines==[]:
        return False
    for att_line in att_lines:
        attachments=[]
        att_chunks=[re.sub('\n','',item) for item in re.split('([.][\sPDFOCXa-z]+)[;\n]',att_line) if "Importance:" not in item and 2<len(item)<90]
        if len(att_chunks)>1:
            for a in range (0,len(att_chunks)-1,2):
                
                if re.findall("\s*[.]\s*[PDFa-z ]+$",att_chunks[a+1])!=[]:
                    attachments.append(''.join(att_chunks[a:a+2]))
                    #attachments.append((att_chunks[a],att_chunks[a+1]))
                    pass
            
            attachment_lists.append(attachments)

        else:
            attachment_lists.append(None)
    return attachment_lists

def getSubjects(emailstext,boo=False):
    subj_names=[]
    things = re.findall("\n\W*[Ss]u.[jl][ea][rc]t[:;\n].*|.*[O0]n.*\n*.*wro.e.", emailstext)
    if boo==True:
        return [thing for thing in things if booOn(thing)==False] 
    elif boo==False:
        if things==[]:
            return False #No subject line found which is not ok in a From:
        elif things!=[]:
            for thing in things:
                if booOn(thing)==True:
                    subj_names.append(False) # No subject line in On: which is ok.
                elif booOn(thing)==False:
                    subj_names0 = re.findall("[Ss]u.[jl][ea][rc]t[:;][\s]*(.*)", thing)
                    if len(subj_names0) == 1 and len(subj_names0[0])>3:
                        subj_names.append(subj_names0[0])
                    else:
                        subj_names.append(None)
        return subj_names

def booOn(email_text):
    ons = re.findall("[O0]+n.*\n*.*wro.e[:;\n]", email_text)
    if ons != []:
        if getTos(email_text)==[False]:
            return True
        else:
            return False
    else:
        return False

def getTS(text,On=True,boo=False,Unix=True,Round=-2):
    
    #regex = json.load(open(Path(pathlib.Path.cwd()/"make_database"/"files"/"regex_uts.json"), 'r'))
    fields_regex={
        "date":["Date[:;]\n*(.*)"],
        "sent":["Sent[:;]\n*(.*)"],
        "on":["On ([A-Z].*[AP][M]).*\n*.* wro[tf]e","On ([A-Z].*2[01][0-9][0-9]).*\n*.*wro[tf]e","On(.*\n*.*)wro.e"]
    }
    regex_lines=[]

    if On==True:
        keys=["date","sent","on"]
    elif On==False:
        keys=["date","sent"]

    for key in keys:
        regex_lines.extend(fields_regex[key])
    regex_line='|'.join(regex_lines)
    hits_list = re.findall(regex_line,text)

    def clean(hit):
        
        regex = json.load(open(Path(pathlib.Path.cwd()/"make_database"/"files"/"regex_uts.json"), 'r'))

        for i in range(0,3):
            for change in regex["timestamp_fixes"]["times"]:
                try:
                    target=re.findall(regex["timestamp_fixes"][0],hit)[0]
                    hit=re.sub(regex["timestamp_fixes"][1],regex["timestamp_fixes"][2],target)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    continue
            
                hit=fix_timestamp(hit)
            for field in ["reg_ex","day","month"]:
                for change in regex["timestamp_fixes"][field]:
                    hit=re.sub(change[0],change[1],hit)

        return hit

    if hits_list==[]: # No timestamp line found
        return False
    else:
        ts_list=[]
        for hits in hits_list:
            try:
                hit_string = [hit for hit in list(hits) if len(hit)>6][0]
                for i in range(0,3):
                    hit_string=clean(hit_string) ### preprocess
                    hit_string=fix_timestamp(hit_string)
                ts_list.append(hit_string)
            except KeyboardInterrupt:
                 raise KeyboardInterrupt
            except:
                # Timestamp line found, but empty/invalid
                ts_list.append(None)
                #print("TIMESTAMP LINE EMPTY:\t",hits_list)

    if boo==True:
        return True

    elif boo==False:
        bad=[]
        if Unix==False:
            return ts_list
        elif Unix==True:
            unix_ts_list=[]
            for ts in ts_list:
                if ts == None:
                    unix_ts_list.append(None)
                else:
                    try:
                        unix_ts = int(dateutil.parser.parse(ts).timestamp())
                        #unix_ts = int(time.mktime(date_time.timetuple()))
                    except:
                        print("CAN NOT READ TIMESTAMP:\t",ts,"\t\t\n")
                        unix_ts=0
                        bad.append(ts)
                    if unix_ts<1262347200 or unix_ts>1514808000: # 2010-2018
                        unix_ts=0
                    if Round==False:
                        unix_ts_list.append(unix_ts)
                    else:
                        unix_ts=round(unix_ts,Round)
                        unix_ts_list.append(unix_ts)
            return unix_ts_list#,bad

# METADATA FIXING FUNCTIONS

def fix_timestamp(TS):
    def timefix1(TS): #fix 12: 15 PM
            #fdig = re.findall(".*20[120][0-9] [012]*[0-9]: [0-9][0-9][\s]*[AP]M",TS)
            test1 = re.findall("[0-9]:\s*[0-9]",TS)
            test2 = re.findall("[0-9]\s*:[0-9]",TS)
            if test1 == [] and test2 ==[]:
                return TS
            elif test1!=[]:
                TSx = re.sub(":\s*",":",TS)
                return TSx
            elif test2!=[]:
                TSx = re.sub("\s*:",":",TS)
                return TSx
    def timefix2(TS): #fix  Thursday November 05  2015 10:1839 AM
            x = re.findall(".*[012]*[0-9]:[0-9][0-9][0-9][0-9][\s]*[AP]M",TS)
            if x == []:
                return TS
            else:
                beg = re.findall("(.*)[012]*[0-9]:[0-9][0-9][0-9][0-9][\s]*[AP]M",x[0])
                hrmn = re.findall(".*([012]*[0-9]:[0-9][0-9])[0-9][0-9][\s]*[AP]M",x[0])
                sec = re.findall(".*[012]*[0-9]:[0-9][0-9]([0-9][0-9])[\s]*[AP]M",x[0])
                end = re.findall(".*[012]*[0-9]:[0-9][0-9][0-9][0-9]([\s]*[AP]M)",x[0])
                full = str(beg[0] + hrmn[0] + ":" + sec[0] + end[0])
                return full
    def timefix3(TS): #fix 3 05 --> 3:05
            x = re.findall(".*[0-9]*[0-9] [0-9][0-9][\s]*[AP]M",TS)
            if x == []:
                return TS
            else:
                beg = re.findall("(.*)[0-9]*[0-9] [0-9][0-9][\s]*[AP]M",x[0])
                #yr = re.findall("()[012]*[0-9] [0-9][0-9][\s]*[AP]M",x[0])
                ti = re.findall(".*([0-9]*[0-9] [0-9][0-9])[\s]*[AP]M",x[0])
                end = re.findall(".*[0-9]*[0-9] [0-9][0-9]([\s]*[AP]M)",x[0])
                gti = re.sub(" ",":",ti[0])
                full = str(beg[0] + gti + end[0])
                return full
    def timefix4(TS): # fix 540 AM --> 5:40 AM
            x = re.findall(".*[0-9]*[0-9][0-9][0-9][\s]*[AP]M",TS)
            if x == []:
                return TS
            else:
                beg = re.findall("(.*)[0-9]*[0-9][0-9][0-9][\s]*[AP]M",x[0])
                hr = re.findall(".*([0-9]*[0-9])[0-9][0-9][\s]*[AP]M",x[0])
                mn = re.findall(".*[0-9]*[0-9]([0-9][0-9])[\s]*[AP]M",x[0])
                end = re.findall(".*[0-9]*[0-9][0-9][0-9]([\s]*[AP]M)",x[0])
                full = str(beg[0] + hr[0] + ":" + mn[0] + end[0])
                return full
    def timefix5(TS): #fix 20156:04 PM --> 2015 6:04 PM
                x = re.findall(".*20[120][0-9][0-9:]+[\s]*[AP]M",TS)
                if x == []:
                    return TS
                else:
                    yr = re.findall("20[012][0-9]",x[0])
                    yr_sp = str((yr[0]) + " ")
                    good = re.sub("20[120][0-9]",yr_sp,x[0])
                    return good
    TS= timefix1(TS)
    TS= timefix2(TS)
    TS= timefix3(TS)
    TS= timefix4(TS)
    TS= timefix5(TS)
    return TS

def fix_name(ogname,people_list,prt=0): # to clean list

    def LikeCanonName(name,people_list,n=0.85):
        for id in people_list:
            for var in people_list[id]["vars"]:
                if re.findall(var,name)!=[]:
                    return people_list[id]["name"]
                
            import difflib
            correctname = difflib.get_close_matches(name,people_list[id]["name"],8,n)
            if correctname !=[]:
                return correctname[0]
        return name

    def RemoveExtraString(name):
        original_name=name
        for range in (0,5):
            name=re.sub("[a-zA-Z.:]+@*[a-zA-Z.]+[.][a-z]+",'',name)
            name=re.sub("mailto:*","",name)
            name = re.sub("[\[\<\(\{].*|\s+\n|[\s\n\W]+$|^[\s\n\W_]+|^ |:|[\w]*@[\w.]*|[0-9]+|~","",name)
            name=re.sub("[A-Z]{2,}","",name)
            name=re.sub("[ ]{2,}"," ",name)
            if len(name)<4:
                return original_name
            else:
                return name
        
    def Caps(name):
        name=name.lower()
        firstletters=re.findall("^[a-z]|[- \'][a-z]",name)
        for i in range(0,len(firstletters)):
            name=re.sub(firstletters[i],firstletters[i].upper(),name,1)
        return name

    def toLastFirst(name):
        import re
        # First Last -> Last, First
        re_firstname="[A-Za-z]{3,}"
        re_lastname="[A-Z\'a-z]{2,}[- ]{0,1}[A-Za-z]+"
        if len(name)>3:
            lastcommafirst = re.findall("^"+re_lastname+"[,.][- ]"+re_firstname+"$",name)
            firstlast=re.findall("^"+re_firstname+" "+re_lastname+"$",name)
            if lastcommafirst != []:
                for lcf in lastcommafirst:
                    lcf=re.sub("[.]",",",lcf)
                    return lcf
            
            elif firstlast != []:

                firstname = re.findall("^("+re_firstname+") "+re_lastname+"$",name)[0]
                lastname = re.findall("^"+re_firstname+" ("+re_lastname+")$",name)[0]
                firstname=re.sub("\n|\'|\"","",firstname)
                firstname=re.sub("\W,",",",firstname)
                firstname=re.sub(" . ","",firstname)
                lastname=re.sub("\n|\'|\"","",lastname)
                lastname=re.sub("\W,",",",lastname)
                lastname=re.sub(" . ","",lastname)
                L_F=lastname+", "+firstname
                return L_F

            elif firstlast == [] and lastcommafirst == []:
                return name
        else:
            return name

    name=ogname
    for i in range(0,3):
        try:
            name=LikeCanonName(name,people_list)
            name=RemoveExtraString(name)
            name=toLastFirst(name)
            name=Caps(name)
        except KeyboardInterrupt:
            raise KeyboardInterrupt

    if ogname!=name and prt==1:
        print("Name fixed:\t",ogname," --> ",name)
    return name

def as_regex(text): # Replace sensitive characters with . for reg ex
    import re
    text=re.sub("[\(\)\[\]\{\}\*\+]|[^\n\w\s]",".",text)
    return text

def lenif(item):
    if type(item)==list:
        return len(item)
    else:
        return 0

def p(p_str,prt):
    if prt==True:
        print(p_str)
    elif prt==False:
        pass
