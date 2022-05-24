import argparse

from naverkin.kin import test_naverkin
from navertoon.toon import test_navertoon
from kofia.crawler import test_kofia
from druginfo.crawler import test_druginfo
from costores.crawler import coscores_search
from naverplace.test import test_naverplace_results_collecting
from fromcurl.crawler import test_fromcurl
from freeproxylists.freeproxy import test_freeproxylists_crawler
from logparser.nginx import test_ngin_log_parser
# from maxmind.geoip import test_maxmind_geoip
from eurosatory.crawler import test_eurosatory
from dcinside.crawler import test_dcinside_crawler

def main():
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Test For crawlite'
    )
    argparser.add_argument('appname', type=str,  help='Input app name for test')
    argparser.add_argument('-keywords', '--keywords', default='')
    argparser.add_argument('-titleId', '--titleId', default='')
    argparser.add_argument('-start_date', '--start_date', default='')
    argparser.add_argument('-end_date', '--end_date', default='')
    argparser.add_argument('-search', '--search', nargs='?', default='')
    argparser.add_argument('-page_range', '--page_range', nargs='?')

    args = argparser.parse_args()
    if args.appname in ['naverkin', 'kin']:
        test_naverkin(args.keywords, args.page_range)
    
    if args.appname == 'navertoon':
        test_navertoon(titleId=args.titleId)
    
    if args.appname == 'kofia':
        test_kofia(
            start_date=args.start_date,
            end_date= args.end_date
        )
    
    if args.appname == 'druginfo':
        test_druginfo(
            q=args.search
        )
    
    if args.appname == 'coscores':
        coscores_search(search=args.search)

    if args.appname == 'naverplace':
        test_naverplace_results_collecting()
    
    if args.appname == 'test_parser':
        from crawlite.utils.parse import extract_json
        content = '''
        }})\\n
                "/adfaoi**/"\njquery({"comment":{"kamapComntcnt":13,"scoresum":52,"scorecnt":13,"currentPage":2,"pageList":[1,2,3],"list":[{"commentid":"4053688","contents":"규가츠 정식은 좋았으나, 스테키정식은 얼려져있던 고기 느낌이 너무 많이 나서 사실 제 입맛에는 아쉬웠어요. 다음에는 규가츠 더블에 다른 메뉴을 먹을꺼 같네요. ","point":3,"username":"호기","profile":"http://k.kakaocdn.net/dn/FHJEP/btqzWqXGrSS/5IkTO9QklZ3yAiTKEnTZf0/img_640x640.jpg","profileStatus":"S","photoCnt":0,"likeCnt":0,"kakaoMapUserId":"157g61f","ownerReply":{},"date":"2021.08.02.","isMy":false,"isBlock":false,"isEditable":false,"isMyLike":false},{"commentid":"3942109","contents":"맛있어요!","point":5,"username":"이승은","profile":"https://p.kakaocdn.net/th/talkp/wm3PnOIuVT/qU4lj8OpKfBF2G3p162YCk/vrcsko_640x640_s.jpg","profileStatus":"S","photoCnt":0,"likeCnt":0,"kakaoMapUserId":"1fhng8q","ownerReply":{},"date":"2021.07.12.","isMy":false,"isBlock":false,"isEditable":false,"isMyLike":false},{"commentid":"3073462","contents":"규카츠 완전 맛있는데 다른 메뉴들도 다 맛있음 ㅠ ㅠ 후라토 전메뉴 다 먹어보는 게 내 소원 . ","point":5,"username":"지연","profile":"https://p.kakaocdn.net/th/talkp/wl2UT2jd9c/UFgRk7OlDThXAo2uIe8fck/f0mwef_640x640_s.jpg","profileStatus":"S","photoCnt":1,"likeCnt":0,"thumbnail":"http://t1.daumcdn.net/local/kakaomapPhoto/review/b643b09f488bf92a00a2b8baf664d5b03b7795b2?original","kakaoMapUserId":"1gbvi0h","photoList":["http://t1.daumcdn.net/local/kakaomapPhoto/review/b643b09f488bf92a00a2b8baf664d5b03b7795b2?original"],"ownerReply":{},"date":"2021.02.09.","isMy":false,"isBlock":false,"isEditable":false,"isMyLike":false},{"commentid":"3073128","contents":"맛있어요!! 다음에 또 방문하고싶네요","point":5,"username":"배현진","profile":"https://p.kakaocdn.net/th/talkp/wmBAKRCXN9/wcIpA3fjkSozc0IAS7WhsK/g949d9_640x640_s.jpg","profileStatus":"S","photoCnt":2,"likeCnt":0,"thumbnail":"http://t1.daumcdn.net/local/kakaomapPhoto/review/64ef0913069a73261665b78b525293b1ebb4f23f?original","kakaoMapUserId":"1gbualh","photoList":["http://t1.daumcdn.net/local/kakaomapPhoto/review/64ef0913069a73261665b78b525293b1ebb4f23f?original","http://t1.daumcdn.net/local/kakaomapPhoto/review/5b41d6ebb85ed2f28837a9f97413b3c90593bf5d?original"],"ownerReply":{},"date":"2021.02.09.","isMy":false,"isBlock":false,"isEditable":false,"isMyLike":false},{"commentid":"3073107","contents":"맛있어요 규카츠맛집!!! 카레에 새우튀김 짱맛있음","point":5,"username":"지현","profile":"https://p.kakaocdn.net/th/talkp/wl4L5mhrYh/lmdT76kLCINSC911aY7gR1/ujsphg_640x640_s.jpg","profileStatus":"S","photoCnt":1,"likeCnt":0,"thumbnail":"http://t1.daumcdn.net/local/kakaomapPhoto/review/61b3bafb4f40a490ec901ad926c0963f1a07ac2f?original","kakaoMapUserId":"1gbtuif","photoList":["http://t1.daumcdn.net/local/kakaomapPhoto/review/61b3bafb4f40a490ec901ad926c0963f1a07ac2f?original"],"ownerReply":{},"date":"2021.02.09.","isMy":false,"isBlock":false,"isEditable":false,"isMyLike":false}]}}); \nxe
        '''

        r = extract_json(content, many=False)
        print(r)
    
    if args.appname ==  'curl_test':
        test_fromcurl()
    
    if args.appname == 'freeproxy':
        test_freeproxylists_crawler()
    
    if args.appname == 'logparser':
        test_ngin_log_parser()
    
    # if args.appname == 'maxmind':
    #     test_maxmind_geoip()

    if args.appname == 'eurosatory':
        test_eurosatory()

    if args.appname == 'dcinside':
        test_dcinside_crawler()

if __name__ == '__main__':
    main()