def K_mean(Document,K,title='제목',*args):
    count=0
    doc=Document.df
    doclist=list(Document.dataframe[title])
    cos_sim=Document.cos_sim()
    
    group=[]
    sample = np.random.choice(doclist,K)
    for paper in sample:
        group.append([paper])
    for paper in doclist:
        if paper not in sample:
            cossim=[]
            for samplepaper in sample:
                cossim.append(cos_sim[samplepaper].loc[paper])
            group[cossim.index(max(cossim))].append(paper)
        else:
            pass
        
    while True:
        count+=1
        newgroup=[]
        sample = np.random.choice(doclist,K)
        for paper in sample:
            newgroup.append([paper])
        for paper in doclist:
            if paper not in sample:
                cossim=[]
                for samplepaper in sample:
                    cossim.append(cos_sim[samplepaper].loc[paper])
                newgroup[cossim.index(max(cossim))].append(paper)
            else:
                pass
            
        if sorted(group)==sorted(newgroup):
            print('end by',count)
            SSE=0
            for gr in group:
                mean=str(set(gr) & set(sample))
                mean=mean.strip("{''}")
                for paper in gr:
                    if paper != mean: SSE=SSE+((1-cos_sim[paper].loc[mean])**2)
            print('SSE: ',SSE)
            return (group,SSE)
        else:
            group=newgroup
            
def tag(Document,Kmeanlist,K,tag='과목',title='제목',*args):
    taged=[]
    for i in Kmeanlist[0]:
        temp=[]
        for j in i:
            index=list(Document.dataframe[title]).index(j)
            temp.append({j:Document.dataframe[tag].loc[index]})
        taged.append(temp)
    return taged