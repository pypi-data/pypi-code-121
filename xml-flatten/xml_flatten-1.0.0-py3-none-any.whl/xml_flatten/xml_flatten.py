xml_flat=[]

def rec(i,x,xpath):
    global xml_flat
    xml_flat.append([xpath, dict([(i.tag,i.text.replace("\n","").replace("\r","").replace("\t",""))]), i.attrib if(len(i.attrib)>0) else ""])
    x=x+len(i)
    xpath = xpath+">"+i.tag
    for j in i:
        if len(j)>0:
            rec(j,x,xpath)
        else:
            xml_flat.append([xpath,dict([(j.tag,j.text)]),j.attrib if(len(j.attrib)>0) else ""])
    return()