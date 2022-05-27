tiers_mapping = {'tier2':2, 'tier3':3,"tier1" : 1,"no tier":4,"1":1,"2":2,"3":3,"4":4}
state_mapping = {'andaman and nicobar islands': '01',
 'chandigarh': '02',
 'dadra and nagar haveli': '03',
 'daman and diu': '04',
 'delhi': '05',
 'jammu and kashmir ': '06',
 'ladakh ': '07',
 'lakshadweep': '08',
 'puducherry': '09',
 'andhra pradesh': '10',
 'arunachal pradesh': '11',
 'assam': '12',
 'bihar': '13',
 'chhattisgarh': '14',
 'goa': '15',
 'gujarat': '16',
 'haryana': '17',
 'himachal pradesh': '18',
 'jammu and kashmir': '19',
 'jharkhand': '20',
 'karnataka': '21',
 'kerala': '22',
 'madhya pradesh': '23',
 'maharashtra': '24',
 'manipur': '25',
 'meghalaya': '26',
 'mizoram': '27',
 'nagaland': '28',
 'odisha': '29',
 'punjab': '30',
 'rajasthan': '31',
 'sikkim': '32',
 'tamil nadu': '33',
 'telangana': '34',
 'tripura': '35',
 'uttar pradesh': '36',
 'uttarakhand': '37',
 'west bengal': '38'}

class Uservector:
  def __init__(self,state=None,tier=None,gender=None,age_group=None,languageId=None ):

    self.state = state
    self.tier = tier
    self.gender = gender
    self.age_group = age_group
    self.languageId = languageId


    '''return embeddings based on input data
    :param string state: Name of the state 
    :param string tier: one of the following(tier1,tier2,tier3,no tier) 
    :param string gender: one of the following (1,2,3)
    :param string age_group: one of the following (0,1,2,3,4)
    :param string languageId: language

    All inputs will be taken in string. In case you have missing values /null send None --> ""
    '''

  def cold_vector_title(self):

        try:
          if self.state is not None:
            state = self.state.lower()
            state_id = str(state_mapping[state])
          else:
            state_id = "99"
        except:
          state_id = "99"

        try:
          if self.tier is not None:
            tier = self.tier.lower()
            tier_id = str(tiers_mapping[tier])
          else:
            tier_id = "9"
        except:
          tier_id = "9"

        try:
          if self.gender is not None:
            gender=str(int(self.gender))
          else:
            gender = "9"
        except:
          gender= "9"
        try:
          if self.age_group is not None:
            age_group=str(int(self.age_group))
          else:
            age_group = "9"
        except:
          age_group = "9"
        try:
          if self.languageId is not None:
            languageId=str(int(self.languageId))
          else:
            languageId = "999"
        except:
          languageId = "999"
        
        title = state_id+tier_id+gender+age_group+languageId
        return title
        
