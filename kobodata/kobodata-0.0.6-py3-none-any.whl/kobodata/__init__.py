import requests
import json

class KoboData:
    def __init__(self,account_domain, data_uuid, token):
        self.account_domain = account_domain
        self.data_uuid = data_uuid
        self.token     = token
    
    @property
    def kobo_data(self):
        url = 'https://{}/api/v2/assets/{}/data/?format=json'.format(self.account_domain, self.data_uuid)
        headers = {'Authorization': 'Token {}'.format(self.token)}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return json.loads(r.content)
        return None

    
    
    @property
    def counts(self):
        data = KoboData(self.account_domain, self.data_uuid, self.token).kobo_data
        return data['count']

    @property
    def get_data(self):
        data = KoboData(self.account_domain, self.data_uuid, self.token).kobo_data
        return data['results']

__doc__ = """

# $ pip3 install kobodata


# Step(1) : import KoboData class
from kobodata import KoboData

# Step(2) : Specify your authentication credentials
# (i) your authentocation token obtained from kobo account settings eg "768fe18a0c1xxxxxxa0c1977a4xxx6ed88

account_token = "xxxxxxxxxxxxxxxxxxxxxxxxx"

# (ii) unique identifier for your dataset e.g "agLCVHnDkbXRkEuhtp4oUF"
dataset_uuid = "xxxxxxxxxxxxxxx"

# (iii) depends on your kobo account type eg: "kf.kobotoolbox.org" or "kobo.humanitarianresponse.info"
account_domain = "xxxxxxxxxxxxxxx"

# Step(3) : Use your KoboData class to access informations as follows
# (i) import the class and specify your credentials
dataset = KoboData(
        account_domain,
        dataset_uuid,
        account_token     
    )


# (ii) to get data, it return a dictionary of your data
my_data = dataset.kobo_data

# (iii) you can convert into a pandas data frame for further analyses
import pandas as pd
table = pd.DataFrame(my_data)
print(table)


# (iv) total number of data collected
print(dataset.counts)


# MIT License
> Programmed by Brightius Kalokola
Email: brightiuskalokola@gmail.com

# Twitter
https://twitter.com/kalokolabr

# Github
https://github.com/kalokola

'I codde to Spread Ideas and make things easier for people.'
"""