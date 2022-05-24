from askdata.human2query import nl2query

if __name__ == "__main__":
    nl = "{{measures.measureA.name}} nel {{entityTypes.entityTypeA.value}}"
    smartquery, version = nl2query(nl, language="en-US")
    print(smartquery)
    print(version)
