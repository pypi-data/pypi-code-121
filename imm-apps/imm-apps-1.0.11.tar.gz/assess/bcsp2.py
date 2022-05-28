from datetime import datetime
from termcolor import colored
from utils import utils
from engine.scoringbc import ScoringBCPNP
import argparse

bcpnp_stream={
    'SW':"Skill_Worker",
    'IG':"International_Graduate",
    'ELSS':'Entry_Level',
    'EESW':'EE_Skill_Worker',
    'EEIG':'EE_International_Graduate'
}
bcpnp_education = {
    0:'Doctor',
    1:'Master',
    2:'Bachelor',
    3:'Post Graduate Certificate or Diploma',
    4:'Trades certification',
    5:'Associate Degree',
    6:'Non-trades certification or Diploma',
    7:'Secondary'
}
bcpnp_education_bonus = {
    0:'BC Post-secondary',
    1:'Canada Post-secondary',  # Outside of BC
    2:'ECA',  # with Education Credential Assessment
    # Successfully completed the Industry Training Authority British Columbia (ITABCs) challenge certification process
    3:'Trade certificate',
    4:'Nothing'
}

bcpnp_region = {
        0:'Stikine',
        1:'Central Coast',
        2:'Northern Rockies',
        3:'Mount Waddington',
        4:'Skeena-Queen Charlotte',
        5:'Powell River',
        6:'Sunshine Coast',
        7:'Kootenay-Boundary',
        8:'Alberni-Clayoquot',
        9:'Kitimat-Stikine',
        10:'Bulkley-Nechako',
        11:'Squamish-Lillooet',
        12:'Strathcona',
        13:'Columbia-Shuswap',
        14:'East Kootenay',
        15:'Peace River',
        16:'Comox Valley',
        17:'Cariboo',
        18:'Central Kootenay',
        19:'Okanagan-Similkameen',
        20:'Cowichan Valley',
        21:'North Okanagan',
        22:'Fraser-Fort George',
        23:'Thompson-Nicola',
        24:'Nanaimo',
        25:'Central Okanagan',
        26:'Capital',
        27:'Fraser Valley',
        28:'Greater Vancouver'
    }

def getParams(args):
    # today=datetime.today()
    # enddate=str(today.year)+'-'+str(today.month)+'-'+str(today.day)
    # startdate=str(today.year-1)+'-'+str(today.month)+'-'+str(today.day)

    oneyear=",".join(args.oneyear or ['0'])
    isworking=','.join(args.isworking or ['0'])
    hourly_rate=",".join(args.rate or ['25'])
    working_hours=",".join(args.hours or ['40'])
    clbs=",".join(args.language or ['5']) 

    stream=bcpnp_stream.get(args.stream,'Skill_Worker') if args.stream else 'Skill_Worker'
    education=bcpnp_education.get(int(args.education),'Bachelor') if args.education else "Bachelor"
    education_bonus=bcpnp_education_bonus.get(int(args.bonus),'ECA') if args.bonus else 'ECA'
    region=bcpnp_region.get(int(args.area),'Greater Vancouver') if args.area else 'Greater Vancouver'
    work_experience=int(args.experience or 0)*12
    params={
        # 'stream':stream,
        'noc':args.noc or '1111',
        'work_experience':work_experience,
        'education':education,
        'education_bonus':education_bonus,
        'has_one_year_canadian_experience':oneyear,
        'is_working_in_the_position':isworking,
        'hourly_rate':hourly_rate,
        'working_hours':working_hours,
        'region':region,
        'clbs':clbs
        
        # 'start_date':args.startdate or startdate,
        # 'end_date':args.enddate or enddate
        }
    return params


def output(data):
    newlist=[]
    for r in list(zip(data['reports'],data['solutions'])):
        unit={**r[0],**r[1]}
        newlist.append(unit)
    newlist.sort(key=lambda x:x.get('total_points'),reverse=True)
    print(colored(f'Totally {len(newlist)} solutions','green'))
    utils.printListDictFields(
        newlist,
        fields=['total_points','clb','hourly_rate','working_hours','is_working_in_the_position','has_one_year_canadian_experience','invited_times','percentage'],
        titles=['Points','CLB','Rate','Hours','Working','One_Year','ITA_Times',"Percentage"]
        )
    print(colored(f'Client facts:','green'))
    record=newlist[0]
    client_facts=[
        ['Education','Bonus','Experience','NOC','Tech Pilot','Region'],
        [record['education'],record['education_bonus'],record['work_experience'],record['noc'],record['tech_pilot'],record['region']]
    ]
    utils.printFList2D(client_facts)

    # ITA analysis 
    # print(colored(f'ITA summary:','green'))
    # record=newlist[0]
    # ita_summary=[
    #     ['From','To','Stream','Total Rounds','Minimum Points','Average Points','Maximum Points'],
    #     [record['start_date'],record['end_date'],record['stream'],record['total_rounds'],record['ita_min'],record['ita_avg'],record['ita_max']]
    # ]
    # utils.printFList2D(ita_summary)


def main():
    parser=argparse.ArgumentParser(description="used for calculating BCPNP Skills Iimmigration points")
    parser.add_argument("-n", "--noc", help="input noc code")
    parser.add_argument("-w", "--isworking", nargs='+',help="adding -w plus 0 1, means is working on the position or not")
    parser.add_argument("-o", "--oneyear",nargs='+', help="adding -o plus 0 1, means with one year direct Canadian experience or not")
    parser.add_argument("-r", "--rate", nargs='+',help="input hourly rates, exmp: 25 26...")
    parser.add_argument("-t", "--hours",nargs='+', help="input working hours per week, exmp: 30 40")
    parser.add_argument("-we", "--experience", help="input direct related work experience years")
    parser.add_argument("-a", "--area", help="optional,default is 28 (Greater Vancouver) input area index")
    parser.add_argument("-e", "--education", help="input educaton index")
    parser.add_argument("-b", "--bonus", help="input education bonus index")
    parser.add_argument("-l", "--language", nargs='+',help="input language clb level")
    parser.add_argument("-i","--information",help="get indexes for area, education, and education bonus",action='store_true')
    parser.add_argument("-sd", "--startdate", help="input begining date. format: 2020-01-01")
    parser.add_argument("-ed", "--enddate", help="input ending date. format: 2020-01-01,Default is today")
    parser.add_argument("-s", "--stream", help="input the stream: SW,IG,ELSS,EESW,EEIG")

    args = parser.parse_args()
    if args.information:
        print(colored('Eduation levels','green'))
        utils.printFDict(bcpnp_education)
        print(colored('Eduation Bonus','green'))
        utils.printFDict(bcpnp_education_bonus)
        print(colored('Regions','green'))
        utils.printFDict(bcpnp_region)
        return 0

    params=getParams(args)
    print(params)
    from copy import deepcopy
    bcsp_data=deepcopy(params)
    for is_working in params['is_working_in_the_position'].split(','):
        for one_year_exp in params['has_one_year_canadian_experience'].split(','):
            for wh in params['working_hours'].split(','):
                for hr in params['hourly_rate'].split(','):
                    for clb in params['clbs'].split(','):
                        bcsp_data['clb']=clb
                        bcsp_data['hourly_rate']=hr
                        bcsp_data['has_one_year_canadian_experience']=bool(one_year_exp)
                        bcsp_data['is_working_in_the_position']=bool(is_working)
                        bcsp_data['working_hours']=float(wh)
                        data=ScoringBCPNP(**bcsp_data)
                        print(data.total_point)
                        # print(data.noc_level_point,'noc level point')
                        # print(data.noc_00_point,'noc_00 point')
                        # print(data.wage_point,'wage_points')
                        # print(data.work_experience_point,'work_experience_point')
                        # print(data.working_in_the_position_point,'working_in_the_position_point')
                        # print(data.one_year_Canadian_work_experience_point,'one_year_Canadian_work_experience')
                        # print(data.educaiton_level_point,'educaiton_level_points')
                        # print(data.education_bonus_point,'education_bonus_points')
                        # print(data.region_point,'region_points')
                        # print(data.language_level_point,'language_level_points')
    # output(data)
   

if __name__=='__main__':
    main()



