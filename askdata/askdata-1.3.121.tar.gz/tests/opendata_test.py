from askdata.smartgraph import smart_opendata, opendata_specific_result


if __name__ == "__main__":
    nl = "wine consumption by countries"
    response = smart_opendata(sentence=nl)
    extraction = opendata_specific_result(response=response, request="top1_df", show=True)
    print(extraction)
