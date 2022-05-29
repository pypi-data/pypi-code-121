with open('damn.txt', 'w') as f:
    print(','.join([str(i) for i in range(10000000, 11000000, 100)]), file=f)
