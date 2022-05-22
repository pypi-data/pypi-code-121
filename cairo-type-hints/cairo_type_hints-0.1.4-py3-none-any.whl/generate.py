from parser import parse


def generate(inputfile, outputfile):
    input = open(inputfile, "r")
    fileContents = input.read()
    result = parse(fileContents)
    output = open(outputfile, "a")
    output.write(result)
    input.close()
    output.close()
