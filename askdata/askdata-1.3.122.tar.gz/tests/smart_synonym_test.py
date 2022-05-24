from askdata.smartgraph import smart_synonyms

if __name__ == "__main__":

    word = "home"
    lang = "en"
    initial_synonyms_list = []

    synonyms, business_name = smart_synonyms(word=word, lang=lang, initial_synonyms_list=initial_synonyms_list)

    print("Synonyms: ")
    print(synonyms)
    print()
    print("Business name:")
    print(business_name)
