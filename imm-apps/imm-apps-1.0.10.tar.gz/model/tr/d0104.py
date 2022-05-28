# before '_' is sheet name
# variable as key, xpath of xml as value. 
data_model={
    'education':{
        "name":"name",
        "education_level":"position",
        "field_of_study":"description"
    },
    'employment':{
        "company":"name",
        "job_title":"position",
        'duties':"description"
    },
    'travel':{
        "destination":"description",
        "purpose":"name",
    }
}
