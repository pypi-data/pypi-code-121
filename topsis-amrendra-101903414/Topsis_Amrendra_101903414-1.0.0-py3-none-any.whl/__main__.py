import sys
import pandas as pd
import numpy as np
import math

def topsis():
 try :
    n = len(sys.argv)

    if n != 5:
        raise ValueError("There should be 5 arguments.")

    if not sys.argv[1].lower().endswith('.csv') or not sys.argv[4].lower().endswith('.csv'):
        raise ValueError("Input and Output file should be in csv format.")

    try:
        df = pd.read_csv(sys.argv[1])
    except:
        print("Unable to read csv.")
        quit()

    if(df.shape[1] <3):
        raise ValueError("Columns in input file should be more than 3")


    if(len(sys.argv[2].split(',')) != len(sys.argv[3].split(','))):
         raise ValueError("Mismatched number of weights and impacts.")


    i=0
    impact_check=sys.argv[3]
    impact_check=impact_check.split(',')
    while i<len(impact_check):
        if impact_check[i] not in ["+","-"]:
            raise ValueError("The impacts should be either '+'/'-'")

        i+=2

    data=df.copy(deep=True)


    #Check for all numeric values

    li=[]
    for i in range(1,len(data.columns)):
        li.append(pd.to_numeric(data.iloc[:,i], errors='coerce').notnull().all())

    if any(li) == False :
        raise ValueError("Values are non-numeric!")

    #Vector Normalization

    for i in data.columns[1:]:
        total = (data[i]**2).sum()
        sqrt=math.sqrt(total)
        data[i]=data[i]/sqrt

    #Weights x Normalized value

    w=sys.argv[2]
    weights=w.split(',')
    weights = list(map(float, weights))

    for i in range(1,len(weights)+1):
        data[data.columns[i]]=data.iloc[:,i]*weights[i-1]

    #Calculating ideal_best,ideal_worst
    i=sys.argv[3]
    impacts=i.split(',')

    ideal_best=[]
    ideal_worst=[]
    for i in range(1,len(impacts)+1):

        if(impacts[i-1]=='+'):
            ideal_best.append(data.iloc[:,i].max())
            ideal_worst.append(data.iloc[:,i].min())

        elif(impacts[i-1]=='-') :
            ideal_best.append(data.iloc[:,i].min())
            ideal_worst.append(data.iloc[:,i].max())

    #Euclidean distance calculation
    dist_best=[]
    dist_worst=[]
    for i in data.index:

        row_values=data.iloc[i,1:]

        diff=list(np.array(row_values) - np.array(ideal_best))
        squared = [number ** 2 for number in diff]
        dist_best.append(math.sqrt(sum(squared)))

        diff=list(np.array(row_values) - np.array(ideal_worst))
        squared = [number ** 2 for number in diff]
        dist_worst.append(math.sqrt(sum(squared)))


    #Calculating performance score or topsis score

    performance=[]
    for i in data.index:
        performance.append(dist_worst[i]/(dist_best[i]+dist_worst[i]))

    df['Topsis Score']=performance
    df['Rank']=df['Topsis Score'].rank(method='dense', ascending=False)

    outputFilename=sys.argv[4]
    df.to_csv(outputFilename,index=False)

 except ValueError as e:
     print(e)

if __name__ == "__main__":
    topsis()
