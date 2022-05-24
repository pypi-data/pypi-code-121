
from nltk.tokenize import TreebankWordTokenizer


class converter:

    def Converter(time_input):
        
        time_input = time_input.replace(":"," ")
        tokenizer = TreebankWordTokenizer()
        time = tokenizer.tokenize(time_input)


        try:
            time[2]
        except:
            print("Enter AM or PM also.")
            exit()
        

        if "AM" in time:
            time.pop(2)
        elif "am" in time:
            time.pop(2)
        elif "Am" in time:
            time.pop(2)
        elif "aM" in time:
            time.pop(2)


        try:
            if "PM" or "Pm" or "pM" or "pm" not in time:
                time[2] = "PM"
        except:
            pass


        if "01" in time and "PM" in time:
            time[0] = "13"
            
        elif "02" in time and "PM" in time:
            time[0] = "14"
            
        elif "03" in time and "PM" in time:
            time[0] = "15"
            
        elif "04" in time and "PM" in time:
            time[0] = "16"
            
        elif "05" in time and "PM" in time:
            time[0] = "17"
            
        elif "06" in time and "PM" in time:
            time[0] = "18"

        elif "07" in time and "PM" in time:
            time[0] = "19"

        elif "08" in time and "PM" in time:
            time[0] = "20"

        elif "09" in time and "PM" in time:
            time[0] = "21"

        elif "10" in time and "PM" in time:
            time[0] = "22"

        elif "11" in time and "PM" in time:
            time[0] = "23"

        elif "12" in time and "PM" in time:
            time[0] = "00"


        if "PM" in time:
            time.pop(2)
        elif "pm" in time:
            time.pop(2)
        elif "Pm" in time:
            time.pop(2)
        elif "pM" in time:
            time.pop(2)


        str1 = ":"
        return (str1.join(time))