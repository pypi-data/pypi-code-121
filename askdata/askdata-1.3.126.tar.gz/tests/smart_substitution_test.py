from askdata.smartgraph import smart_substitution

if __name__ == "__main__":

    sentence = "monuments <mask> Italy"
    new_sentence = smart_substitution(sentence=sentence, language="en")
    print(new_sentence)
