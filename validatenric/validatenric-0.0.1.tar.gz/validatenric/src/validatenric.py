#!/usr/bin/env python

def validate(NRIC):
    
    NRIC = NRIC.upper()
    
    val_letters = ["S", "T", "F", "G"]
    dict1 = {0:"J", 1:"Z", 2:"I", 3:"H", 4:"G", 5:"F", 6:"E", 7:"D", 8:"C", 9:"B", 10:"A"}
    dict2 = {0:"X", 1:"W", 2:"U", 3:"T", 4:"R", 5:"Q", 6:"P", 7:"N", 8:"M", 9:"L", 10:"K"}    
    
    if type(NRIC) == str and NRIC[1:8].isdigit() and NRIC[0] in val_letters and len(NRIC) == 9:

        char = [i for i in NRIC] 
    
        total = int(char[1])*2 + int(char[2])*7 + int(char[3])*6 + int(char[4])*5 + int(char[5])*4 + int(char[6])*3 + int(char[7])*2

        if char[0] == "T" or char[0] == "G":
            total = total+4

        rem = total % 11

        if char[0] == "S" or char[0] == "T":
            IC_dict = dict1
        else:
            IC_dict = dict2

        if IC_dict[rem] == char[8]:
            return "valid"
        else:
            return "invalid, wrong checksum"
    
    else:
        return "invalid, wrong format"
    