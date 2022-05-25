from deampy import in_out_functions as OutSupport


myList = [['Col1', 'Col2', 'Col3', 'Col4']]
#myList.append(['s1', 's2', 's3'])
#myList.append(['A', '-100', '1,000'])

for i in range(1, 10):
    myList.append(['row'+str(i), i, 2*i, 3*i])

OutSupport.write_csv(file_name ='myCSV.csv', rows=myList, directory='CSVFolder')
