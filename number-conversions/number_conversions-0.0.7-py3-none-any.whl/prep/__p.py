"""
Inside truth.txt, is an extract of the body tag from https://en.wikipedia.org/wiki/List_of_numeral_systems dated
2022-05-02.
Your task is to extract the standard positional numeral systems. Extract base and the name

Found in a .wikitable below a h3 with a span inside with id id="Standard_positional_numeral_systems"

"""
from typing import Dict, List
import re


def extract_details(text: str) -> List[Dict[str, str]]:
    number_systems = []

    # get the table
    text = text.translate(str.maketrans('', '', '\n'))

    table = re.search(
        r'<h3><span.*?id="Standard_positional_numeral_systems".*?<table class="wikitable">(?P<tbody>.*?)</table>',
        text,
    )

    if 'tbody' in table.groupdict().keys():
        table_body = table.group('tbody')
        """
            shall store retrieved number systems in the form 
            [
                {
                    'base': 2,
                    'system': 'Binary Number',
                    'system_name': 'Binary'
                }
            ]            
        """

        # all rows in the table
        table_rows_itr = re.finditer(r'<tr>.*?<td>(?P<base>\d+)</td>.*?<td>(?P<sys>.*?)</td>', table_body)

        for table_row_match in table_rows_itr:
            nms_dict = table_row_match.groupdict()

            if nms_dict:
                trident = {
                    'base': nms_dict.get('base'),
                    'system': nms_dict.get('sys'),
                    'system_name': nms_dict.get('sys')
                }

                if '<a href=' in nms_dict.get('sys'):
                    system_x = re.search(r'title="(?P<sys>.*?)">(?P<sys_name>\w+)</a>', nms_dict.get('sys'))
                    sys_dict = system_x.groupdict()

                    if sys_dict:
                        trident.update({
                            'system': sys_dict.get('sys').replace(' (page does not exist)', ''),
                            'system_name': sys_dict.get('sys_name')
                        })

                number_systems.append(trident)

    return number_systems


with open('truth.txt', 'r', encoding='utf-8') as file:
    details = extract_details(file.read())

    with open('systems.csv', 'w') as w_file:
        title = 'base,system,system_name'
        print(title, file=w_file)
        lines = '\n'.join(
            map(lambda detail: f"{detail.get('base')},{detail.get('system')},{detail.get('system_name')}", details)
        )
        print(lines, file=w_file)
