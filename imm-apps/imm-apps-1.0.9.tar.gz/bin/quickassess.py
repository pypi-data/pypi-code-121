# from context import BASEDIR
import argparse
from tabulate import tabulate
from termcolor import colored
import os
import json
import requests
from dotenv import dotenv_values
from assess.engine.quickassessmodel import QuickAssessModel
from datetime import date,datetime
import warnings
warnings.filterwarnings("ignore")

api_url = "https://jackyzhang.pro/assess/quick/"

def education_level(level):
    edu_level={
        'Doctor':["Doctor"],
        'Master':["Master"],
        'Bachelor': ["Post-graduate diploma",'Bachelor'],
        'Diploma':["Associate","Diploma/Certificate"],
        'Secondary':["High School"],
        'Other':["Less than high school"]
        }
    for el,l in edu_level.items():
        if level in l:
            return el;


def getData(excel_file):
    data = QuickAssessModel(
        excels=[excel_file]).dict()
    data = data['facts']
    level=data['level']

    return_data = {
        "basic": {
            "dob": data['dob'].strftime("%Y-%m-%d"),
            "email": "jacky@gmail.com",
            "phone": "7783215110",
            "lastName": "Zhang",
            "firstName": "Jacky",
            "birthCity": "Nanjing",
            "birthCountry": "China"
        },
        "language": {
            "date": date.today().strftime('%Y-%m-%d'),
            "reading": data['reading'] if data['reading'] else 0,
            "writting": data['writting'] if data['writting'] else 0,
            "speaking": data['speaking'] if data['speaking'] else 0,
            "listening": data['listening'] if data['listening'] else 0,
            "testFormat": data['test_format'] if data['test_format'] else "IELTS"
        },
        "education": {
            "level": education_level(level),
            "country": data['edu_country'],
            "province": data['edu_province'],
            "institute": "NJU",
            "graduateDate": data['graduate_date'].strftime('%Y-%m-%d')
        },
        "family": [
            {
                "dob": data['relative_dob'].strftime("%Y-%m-%d") if data['relative_dob'] else datetime.today().strftime("%Y-%m-%d"),
                "city": "Vancouver",
                "name": "Li",
                "province": data['relative_province']if data['relative_province'] else "BC",
                "canadaStatus": data['canada_status'] if data['canada_status'] else "PR",
                "relationship": data['relationship'] if data['relationship'] else "spouse"
            }
        ],
        "assets": {
            "liquidAssets": data['liquid_assets'] if data['liquid_assets'] else 0,
            "netWorth": data['net_worth'] if data['net_worth'] else 0
        },
        "workExperience": {
            "startDate": data['start_date'].strftime('%Y-%m-%d'),
            "endDate": data['end_date'].strftime('%Y-%m-%d'),
            "noc": data['work_noc'],
            "term": data['term'],
            "country": data['work_country'],
            "jobTitle": data['job_title'],
            "province": data['work_province'],
            "sharePercentage": data['share_percentage']
        },
        "adaptation": {
            "noc": data['joboffer_noc'] if data['joboffer_noc'] else '1123',
            "title": "Marketing specialist",
            "jobOffer": data['job_offer'],
            "province": data['joboffer_province'] if data['joboffer_province'] else "BC"
        }
    }
    return return_data


def getSolutions(data):
    path=os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))
    config = dotenv_values(path)
    token = config['TOKEN']
    headers = {
        'Authorization': f"Token {token}",
        'Content-Type': 'application/json'
    }
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f' Response status code is {response.status_code}, and there is no feedback')


def showData(solutions,args):
    if solutions:
        print(colored('You may be qualified for the Canadian immigration programs as the following\n', 'green'))
        for prog in solutions:
            print(colored("* {program} *".format(**prog), 'green'))
            print(colored("Stream: ","green"),colored("{stream}".format(**prog), 'white'))
            if args.description: print(colored("Description: ","green"),colored("{description}".format(**prog), 'white'))
            if args.remark: print(colored("Remark: ","green"),colored("{remark}".format(**prog), 'white'))
    else:
        print(colored("You are not qualified for any program","red"))


def main():
    parser = argparse.ArgumentParser(
        description="used for processing everything noc related")
    parser.add_argument("-e", "--excel", help="input excel file")
    parser.add_argument(
        "-j", "--json", help="print json data ", action='store_true')
    parser.add_argument(
        "-d", "--description", help="print program description data ", action='store_true')
    parser.add_argument(
        "-r", "--remark", help="print program remark data ", action='store_true')

    args = parser.parse_args()

    if args.excel:
        data = getData(args.excel)
        solutions=getSolutions(data)
        showData(solutions,args)
        if args.json:
            print(json.dumps(data, indent=3))


if __name__ == "__main__":
    main()
