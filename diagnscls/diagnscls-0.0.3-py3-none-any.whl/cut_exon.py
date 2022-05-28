import os

NUMBER_OF_EXON = 28
exons = [""] * 29
def cut(file_name):
    f = open(os.path.join(os.getcwd(), 'consensus_{}.txt'.format(file_name)), 'r')
    exon_index_file = open("exon_index.txt","r")
    data = f.readline()
    start_index = int(exon_index_file.readline().split(" ")[2])+5
    for i in range(0,NUMBER_OF_EXON):
        line = exon_index_file.readline()
        start_idx = start_index + int(line.split(" ")[2]) + 47
        end_idx = start_index + int(line.split(" ")[4]) + 47
        exons[i+1] = data[start_idx:end_idx+1]

        # print(f">> EXON[{i+1}] -> " + "start: " + str(start_idx)+", end: " + str(end_idx) + ", len: " + str(end_idx - start_idx))

        exon_integrated = ""

    for j in range(0,NUMBER_OF_EXON):
        exon_integrated += exons[j+1]

    exon_integrated = exon_integrated.upper() 
    exon_index_file.close()
    f.close()

    write_file = open('exon_{}.txt'.format(file_name), 'w')
    write_file.write(exon_integrated)
    write_file.close()

