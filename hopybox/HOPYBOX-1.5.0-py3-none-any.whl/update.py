from .hopter import Error_pta
data_date = {
'0.0.1':'May 2, 2022',
'0.0.5':'May 2, 2022',
'1.0.0':'May 6, 2022',
'1.3.4':'May 15, 2022',
'1.4.7':'May 27, 2022',
'1.4.8':'May 28, 2022',
'1.4.9':'May 28, 2022',
'1.5.0':'May 28, 2022',
}

data_main = {
'1.4.7':'• Update help document style\n• Fixed some known issues',
'1.4.8':'• Improve the help documentation\n• Added version display\n• Fixed some known issues',
'1.4.9':'• Fixed some known issues',
'1.5.0':'• Added program update log\n• Fixed some known issues',
}

def look_for_data(version):
  try:
    print('\033[96mHOPYBOX {} Update Data\033[0m\033[92m ({})\033[0m\n\033[94m{}'.format(version,data_date[version],data_main[version]))
  except KeyError as e:
    Error_pta('KeyError','Command','No changelog found for this version','update '+version)