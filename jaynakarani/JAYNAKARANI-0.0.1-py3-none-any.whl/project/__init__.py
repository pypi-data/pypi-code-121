def validation (gst):
    count=0
    a=[]
    a[:0]=gst
    #print(type(a[0]))
    if len(a)!=15:
        print("invalid")
    else:
        if a[0]=="0" or a[0]=="1" or  a[0]=="2" or  a[0]=="3":
            count=count+1
        # if a[1]=="0" or a[1]=="1" or  a[1]=="2" or  a[1]=="3"or a[1]=="4" or a[1]=="5" or  a[1]=="6" or  a[1]=="7" or  a[1]=="8" or  a[1]=="9":
        #     count=count+1
        if a[1].isdigit():
            count = count + 1
        for x in range(2,7):
            # print(a[x])
            if a[x].isalpha():
                count = count + 1
        # print("secon loop")
        for x in range(7,11):
            # print(a[x])
            if a[x].isdigit():
                count = count + 1
        # print("end loop")
        if a[11].isalpha():
            count = count + 1
        if a[12].isdigit():
            count = count + 1
        if a[13]=="z":
            count = count+1
        if a[14].isdigit():
            count = count + 1
        if count==15:
            print("valid")
        else:
            print("invalid")
# validation("25asdfg1234a2z2")