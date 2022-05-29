import requests
import user_agent
import json
import uuid
import re
import random
import bs4
import hmac, hashlib, urllib, stdiomask, urllib.request, uuid
from user_agent import generate_user_agent
from uuid import uuid4
from bs4 import BeautifulSoup





class Hunter:
	def Gmail(email: str) -> str:
		eml = email.replace('@gmail.com','')
		headers = {
	    'accept': '*/*',
	    'accept-encoding': 'gzip, deflate, br',
	    'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
	    'content-length': '3911',
	    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
	    'cookie': 'OGPC=422038528-2:; SID=8Ae5CNXyYLku7h3Nhd6PmjEwsqpLep9sdfcDc_QeJT1m6pf_cFdWBefOdFWBrRatzQzoTw.; __Secure-3PSID=8Ae5CNXyYLku7h3Nhd6PmjEwsqpLep9sdfcDc_QeJT1m6pf_LWBgOEuV0LWH29_CLb3l1g.; HSID=A8KaTqMCOG6xpfvsz; SSID=AtYd81IgyZuE9EbfE; APISID=E3Psm5Uangi4fH9M/AkOnPYEUZWnD-tnA_; SAPISID=iN7Q0OqbHZcyy5FL/Aerh1_4xeYlLJY4Hq; __Secure-3PAPISID=iN7Q0OqbHZcyy5FL/Aerh1_4xeYlLJY4Hq; ACCOUNT_CHOOSER=AFx_qI6QfbFWoV6PV6XKN_T6BDu29QAEvMrEZsoAl1r4bDBfnWApbNKbPlRCbFUWBfZ_IufZlpgrXPJIQyLZtlrdzhTBLG1ugbS2CJ2q9HNMMkzfgeaXgctISpVwNdXddAWu4ZnL0x6TC4OCJGrmngsaE5GSmcovCQ; LSID=o.myaccount.google.com|s.youtube:8Ae5CGkVX0iajA0zvRf3mhX7pmhByOogOBptOhnbeOOuoJS6lsMzh7eIoJ7jRz_OOQU1DQ.; SEARCH_SAMESITE=CgQImZIB; __Host-3PLSID=doritos|o.myaccount.google.com|s.youtube:8Ae5CGkVX0iajA0zvRf3mhX7pmhByOogOBptOhnbeOOuoJS6ByLMNjL9oNzA97kBg7BANg.; 1P_JAR=2021-03-29-09; NID=212=i268DCPkYi3AzR0f25yIGeJwDvI9KnX0IkpB6-jLiMgIkylu-ok0FxsNwgb77pnNf9P1dRbBa0rwmwoo3rBZLPEqBaYbIUTYOqnGXlodQyFP6PiO7x1DARyLyIg2nH_J_J208rXWq1sLL7oP_YSeJFznofwfpsHamypEYMgwPx2rU9UJJ59txYOFOliHngVgrmyLeujCj_dKNV8hrTJDFTTVfnxZG68C; __Host-GAPS=1:BWYU84SbcmvuPTxMnLb_Bw1WhSze11euoEbasRquyke84p3z6kKhM4STn2l2KqDaXmLnjmuLAu5YjxpgPYYS2MAbFJoYEA:8QsfUKnQPG8GNFFh; SIDCC=AJi4QfGikn_BfUsmrNc_AQgbrwCzKzaBTYlqHvZ_vt7pRS98qOGuitJ1M1_khzvPELS_owtDIQ; __Secure-3PSIDCC=AJi4QfH3OD5jfNAacCFyT0_heunei0GLdQymhUmRU8zPB7R7Svse8_GiuWLuXbaSblXAYlq-7bU',
	    'google-accounts-xsrf': '1',
	    'origin': 'https://accounts.google.com',
	    'referer': 'https://accounts.google.com/signin/v2/identifier?continue=https%3A%2F%2Fadssettings.google.com%2Fauthenticated%3Fref%3Dyt_auth%26pli%3D1&ec=GAlAmQM&flowName=GlifWebSignIn&flowEntry=AddSession',
	    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
	    'sec-ch-ua-mobile': '?0',
	    'sec-fetch-dest': 'empty',
	    'sec-fetch-mode': 'cors',
	    'sec-fetch-site': 'same-origin',
	    'user-agent': str(generate_user_agent()),
	    'x-chrome-id-consistency-request': 'version=1,client_id=77185425430.apps.googleusercontent.com,device_id=eaa94017-90e6-4761-a779-143e63ce180a,sync_account_id=116486990055578668701,signin_mode=all_accounts,signout_mode=show_confirmation',
	    'x-client-data': 'CJa2yQEIo7bJAQjEtskBCKmdygEIlqzKAQiIucoBCIbCygEI+MfKAQjx6soBCLGaywEI1JzLAQjjnMsBCKmdywEY4ZrLAQ==',
	    'Decoded':'message ClientVariations {// Active client experiment variation IDs. repeated int32 variation_id = [3300118, 3300131, 3300164, 3313321, 3315222, 3316872, 3318022, 3318776, 3323249, 3329329, 3329620, 3329635, 3329705]; // Active client experiment variation IDs that trigger server-side behavior. repeated int32 trigger_variation_id = [3329377];}',
	    'x-same-domain': '1' }
	
		data = {
        'continue': 'https://mail.google.com/mail',
        'hl': 'ar',
        'service': 'mail',
        'dsh': 'S-1123097581:1631528304749024',
        'f.req': f'["AEThLlz_VT1jjcGOzsagHCKd9TxpvtSL5VW_PSDl9G3PGW9X6vZPw_D-ydy7JSvwGVI8zdE1Pbt9AaDrdbU2l_xxgwnNru0s6wYm8u9CB-7TKM96P4S16w_rbjAKuc3vKV3fi85GIqA1H7miG79yEdbc7N-5BjDZGQV_S8fWlUDRJKOQm8z2ehY2-Cy-u3QY9Iw7phzV93B6XdQ8yIW_OkS_tsJJGKh_sw","ali","mao","{eml}",true,"S-1123097581:1631528304749024",1]',
        'at': 'AFoagUVfeo8LVbsN3fYDFmYlF9KRimMUSg:1631528356498',
        'azt': 'AFoagUXFZ-eGXSAczqeEHzn2L1JFqNyEWw:1631528356498',
        'cookiesDisabled': 'false',
        'deviceinfo': '[null,null,null,[],null,"IQ",null,null,null,"GlifWebSignIn",null,[null,null,[],null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,[5,"77185425430.apps.googleusercontent.com",["https://www.google.com/accounts/OAuthLogin"],null,null,"c6264e90-8773-4846-81ef-2445a4586cc3",null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,5,null,null,[],null,null,null,[],[]],null,null,null,null,null,null,[],null,null,null,[],[]],null,null,null,null,2,null,false,1,""]',
        'gmscoreversion': 'undefined'}
        
		response = requests.request("POST", 'https://accounts.google.com/_/signup/webusernameavailability?hl=ar&_reqid=547979&rt=j', data=data, headers=headers).text
		return response


		
	def Hotmail(email: str) -> str:
		headers = {
	    'Accept': '*/*',
	    'Content-Type': 'application/x-www-form-urlencoded',
	    'User-Agent': str(generate_user_agent()),
	    'Connection': 'close',
	    'Host': 'odc.officeapps.live.com',
	    'Accept-Encoding': 'gzip, deflate',
	    'Referer': 'https://odc.officeapps.live.com/odc/v2.0/hrd?rs=ar-sa&Ver=16&app=23&p=6&hm=0',
	    'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
	    'canary': 'BCfKjqOECfmW44Z3Ca7vFrgp9j3V8GQHKh6NnEESrE13SEY/4jyexVZ4Yi8CjAmQtj2uPFZjPt1jjwp8O5MXQ5GelodAON4Jo11skSWTQRzz6nMVUHqa8t1kVadhXFeFk5AsckPKs8yXhk7k4Sdb5jUSpgjQtU2Ydt1wgf3HEwB1VQr+iShzRD0R6C0zHNwmHRnIatjfk0QJpOFHl2zH3uGtioL4SSusd2CO8l4XcCClKmeHJS8U3uyIMJQ8L+tb:2:3c',
	    'uaid': str(uuid4()),
	    'Cookie': 'xid=d491738a-bb3d-4bd6-b6ba-f22f032d6e67&&RD00155D6F8815&354'}
	
		response = requests.request("POST", "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=0&emailAddress=" + str(email) + "&_=1604288577990", data=False, headers=headers)
		if str('Neither') in str(response.text):
			massage = {'status':'Successful','Telegram':'@SidraELEzz'}
			return massage
 
		else:
			massage = {'status':'null[]null','Telegram':'@SidraELEzz'}
			return massage
			
		
	def Yahoo(email: str) -> str:
		eml = email.replace('@yahoo.com','')
		headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '17973',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'APID=UP139a7583-ebf0-11eb-b505-06ebe7a65878; B=1gu92j5gg4sv7&b=3&s=64; A1=d=AQABBCoF-2ACEDfMWHRNdZQ9oaAHUO4YHqMFEgEBAQFW_GAEYQAAAAAA_eMAAAcI53MCYZkieRg&S=AQAAAuJmx1yIDVMiY71k2AGooYk; A3=d=AQABBCoF-2ACEDfMWHRNdZQ9oaAHUO4YHqMFEgEBAQFW_GAEYQAAAAAA_eMAAAcI53MCYZkieRg&S=AQAAAuJmx1yIDVMiY71k2AGooYk; GUC=AQEBAQFg_FZhBEIc3QQ6; cmp=t=1627550703&j=0; APIDTS=1627550737; A1S=d=AQABBCoF-2ACEDfMWHRNdZQ9oaAHUO4YHqMFEgEBAQFW_GAEYQAAAAAA_eMAAAcI53MCYZkieRg&S=AQAAAuJmx1yIDVMiY71k2AGooYk&j=WORLD; AS=v=1&s=9z9sgq95&d=A6103d241|eavlddr.2Sqtm1snR4vumZPgWEv2CX8ETv8qsCVpXUOAi6BcDaqYAawFRdXZOH3x1ZhIOOPANiSybHZ1j1IBJfKp_yUQeVT2a7U2iFeceXk3DV8Yf6fdA4Mb3M_1A3WY2rpfLpkN2geA1AHRb_QuK0p_gvRBC25hCJqX6_BqNWBCQZ40y2vcTOUrMHZQRGCPbygJ4jCC1pmj16D_TNVaFo68GkkgrxHiFpLQEP9zBsfEM9g8FM8Qd3Gs8oJHQRyvyel09x3uEdniEFCXR93nRCcOMMKCI7xvW239gVcz1Gs_5hmZv6aql00Zge0HJaK6YKPDg9Q7rFfMe7pJry4gCuNMiq_bH9TeBHQEGjqLCJR_d8hcSFHxUnNah4D8.hwV7o1hyYUKQl2Pw6aVKPizRyscmuz0Rwa1LUKGV0O2ls2MSsR4g4TzVlLObvUuKBdrdIJJD3Em1NsNsXKj3uyr.XgZV3E09rJQbldIcePNMPkT7jJjydoGuIBVbqutW0MgHN5IShbRcy6cVifEmil4551or5xaGO5kNpIDCbjUmhD8.MnIfBGRlSIITVGGoQhj3l5TBA742dFc_zcZJmtF5XIrHTr_wMpbpc3ZzD1SgWTDMvySFcsTwH8DdIPhUw4c5QUfyh0kECQFV6OG2M9B06c1wayVg_OiVhy6B6u8Q5AHjbRhsacLtI8K7KxG3JA6oxXmOla3MUX35XvU2axN9DChrM3gpJlJYgmqxV454FF23dysnz4sixK8tvwUc.4EiOU_5OfNGmgZpA.MiCif_oYX3m92DAi38QIl~A',
        'Host': 'login.yahoo.com',
        'Origin': 'https://login.yahoo.com',
        'Referer': 'https://login.yahoo.com/account/create?.lang=ar-JO&src=homepage&specId=yidReg&done=https%3A%2F%2Fwww.yahoo.com',
        'Sec-Ch-Ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': str(generate_user_agent()),
        'X-Requested-With': 'XMLHttpRequest'}
        
		data = {
        'browser-fp-data': '{"language":"en-US","colorDepth":24,"deviceMemory":8,"pixelRatio":1,"hardwareConcurrency":2,"timezoneOffset":-180,"timezone":"Asia/Baghdad","sessionStorage":1,"localStorage":1,"indexedDb":1,"openDatabase":1,"cpuClass":"unknown","platform":"Win32","doNotTrack":"unknown","plugins":{"count":3,"hash":"e43a8bc708fc490225cde0663b28278c"},"canvas":"canvas winding:yes~canvas","webgl":1,"webglVendorAndRenderer":"Google Inc.~Google SwiftShader","adBlock":0,"hasLiedLanguages":0,"hasLiedResolution":0,"hasLiedOs":0,"hasLiedBrowser":0,"touchSupport":{"points":0,"event":0,"start":0},"fonts":{"count":49,"hash":"411659924ff38420049ac402a30466bc"},"audio":"124.04347527516074","resolution":{"w":"1366","h":"768"},"availableResolution":{"w":"728","h":"1366"},"ts":{"serve":1627553991633,"render":1627553997166}}',
        'specId': 'yidreg',
        'crumb': 'rak/FdAmWa5',
        'acrumb': '9z9sgq95',
        'done': 'https://www.yahoo.com',
        'attrSetIndex': '0',
        'tos0': 'oath_freereg|xa|ar-JO', 
        'yid': str(eml),
        'password': 'https://t.me/SidraTools',
        'shortCountryCode': 'AF',}
        
		response = requests.request("POST", 'https://login.yahoo.com/account/module/create?validateField=yid', data=data, headers=headers)
		if str('"birthDate"') in str(response.text):
			massage = {'status':'Successful','Telegram':'@SidraELEzz'}
			return massage
			
		else:
			massage = {'status':'null[]null','Telegram':'@SidraELEzz'}
			return massage
			
		
	def Aol(email: str) -> str:
		eml = email.replace('@aol.com','')
		headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '18536',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'BX=05cdflhgh88dv&b=3&s=fa; GUC=AQEBAQFhFXNhHkIeKASA; rxx=230ufm9rd1p.2ffkvhk6&v=1; A1=d=AQABBL8hFGECEA1iv_3z3cem0COBi6yvsQIFEgEBAQFzFWEeYQAAAAAA_eMAAAcIvyEUYayvsQI&S=AQAAAngb50-m21aCLls9vcsvdIA; A3=d=AQABBL8hFGECEA1iv_3z3cem0COBi6yvsQIFEgEBAQFzFWEeYQAAAAAA_eMAAAcIvyEUYayvsQI&S=AQAAAngb50-m21aCLls9vcsvdIA; A1S=d=AQABBL8hFGECEA1iv_3z3cem0COBi6yvsQIFEgEBAQFzFWEeYQAAAAAA_eMAAAcIvyEUYayvsQI&S=AQAAAngb50-m21aCLls9vcsvdIA&j=WORLD; AS=v=1&s=9Ach1eVW&d=A6115734a|.jJjUM3.2Sq6mpRaeUvGOFaxkilDMMNq9Ri7WiuICAYOOQc8JzylVD7TqAyOQXyoGr3xjU5It2l8d2Tm2XplfzH_3CxVMv80ojV9Z2.2KK3pELyejomUkEej8.XfKekex.Y8YC.aN2I_2SK8dJrsij_oAiqz0F5q_AxGBEXANzyyOUk4SZBvgOyRlOVZZfqe1tH9zRhKo2pZ1sSrbHl3et7WTdq75c9ftrqF99EdnVhfX55FDU1s18vjW7yhqwnAR4wuzvLUp53LxbG0XAVElc29r1qDyJ5FaMTplnZzc8qs73k0YQ5CBNdeyLQh6_xlUZDPF3EaPrn9XaJEL_IRPJTt9lh7cFMDyMygjEjL3c9.vDyB7bwl6yDEgtWrB0TolID0D_m3WNruvGdsfqqTKHJO.tFLx00tnx_aYJqqVhmRTi_UgdGMAwv_Ns3eT_Ole8uf5okFWiVAN1Att2io_NuZsS3h6kOWMkER6k3h2isdL4pnCJPoskQTs2gDRo.CaRjcNBQk_v985XvaIGGYsw3Kcgm0ZZk.ni3fv.4uUvpxB431Xi_LLXeObPrKXrlLMVNiiAGEwv.0m5TtV41ib11dBba3jtsohTqUZpwIYEU4M4KF3G_N.2SfLRVYMUiNgOlO2ZLmxQmfWGPdysVpSo.UlJUUqEbKPZzJpH4Y_z8BWOeSjIEW9XOKCyf.ZeoXJufQVU5oS1V0_PydswVuYN7c2dOvWA.E7jrTMlPo3ZzaqshPohpubodq8ofYN9UowbOL8eYnyIKny.YvjJb6KLrCr0jersbNU1Z3pBHQutbA9l2iyl4RkMs01sRnL2PVa94n42RmMIEiVYvecUGO~A',
        'Host': 'login.aol.com',
        'Origin': 'https://login.aol.com',
        'Referer': 'https://login.aol.com/account/create?intl=us&src=fp-us&.done=https%3A%2F%2Fapi.login.aol.com%2Foauth2%2Fauthorize%3Fclient_id%3Ddj0yJmk9ZXRrOURhMkt6bkl5JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWQ2%26intl%3Dus%26nonce%3DkYrCBuoE3NhBcpMPi7iWi4QTnplDEgs0%26redirect_uri%3Dhttps%253A%252F%252Foidc.www.aol.com%252Fcallback%26response_type%3Dcode%26scope%3Dmail-r%2Bopenid%2Bopenid2%2Bsdps-r%26src%3Dfp-us%26state%3DeyJhbGciOiJSUzI1NiIsImtpZCI6IjZmZjk0Y2RhZDExZTdjM2FjMDhkYzllYzNjNDQ4NDRiODdlMzY0ZjcifQ.eyJyZWRpcmVjdFVyaSI6Imh0dHBzOi8vd3d3LmFvbC5jb20vIn0.hlDqNBD0JrMZmY2k9lEi6-BfRidXnogtJt8aI-q2FdbvKg9c9EhckG0QVK5frTlhV8HY7Mato7D3ek-Nt078Z_i9Ug0gn53H3vkBoYG-J-SMqJt5MzG34rxdOa92nZlQ7nKaNrAI7K9s72YQchPBn433vFbOGBCkU_ZC_4NXa9E&specId=yidReg&done=https%3A%2F%2Fapi.login.aol.com%2Foauth2%2Fauthorize%3Fclient_id%3Ddj0yJmk9ZXRrOURhMkt6bkl5JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWQ2%26intl%3Dus%26nonce%3DkYrCBuoE3NhBcpMPi7iWi4QTnplDEgs0%26redirect_uri%3Dhttps%253A%252F%252Foidc.www.aol.com%252Fcallback%26response_type%3Dcode%26scope%3Dmail-r%2Bopenid%2Bopenid2%2Bsdps-r%26src%3Dfp-us%26state%3DeyJhbGciOiJSUzI1NiIsImtpZCI6IjZmZjk0Y2RhZDExZTdjM2FjMDhkYzllYzNjNDQ4NDRiODdlMzY0ZjcifQ.eyJyZWRpcmVjdFVyaSI6Imh0dHBzOi8vd3d3LmFvbC5jb20vIn0.hlDqNBD0JrMZmY2k9lEi6-BfRidXnogtJt8aI-q2FdbvKg9c9EhckG0QVK5frTlhV8HY7Mato7D3ek-Nt078Z_i9Ug0gn53H3vkBoYG-J-SMqJt5MzG34rxdOa92nZlQ7nKaNrAI7K9s72YQchPBn433vFbOGBCkU_ZC_4NXa9E',
        'Sec-Ch-Ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': str(generate_user_agent()),
        'X-Requested-With': 'XMLHttpRequest'}
        
		data = {
        'browser-fp-data': '{"language":"en-US","colorDepth":24,"deviceMemory":8,"pixelRatio":1,"hardwareConcurrency":2,"timezoneOffset":-180,"timezone":"Asia/Baghdad","sessionStorage":1,"localStorage":1,"indexedDb":1,"openDatabase":1,"cpuClass":"unknown","platform":"Win32","doNotTrack":"unknown","plugins":{"count":3,"hash":"e43a8bc708fc490225cde0663b28278c"},"canvas":"canvas winding:yes~canvas","webgl":1,"webglVendorAndRenderer":"Google Inc.~Google SwiftShader","adBlock":0,"hasLiedLanguages":0,"hasLiedResolution":0,"hasLiedOs":0,"hasLiedBrowser":0,"touchSupport":{"points":0,"event":0,"start":0},"fonts":{"count":49,"hash":"411659924ff38420049ac402a30466bc"},"audio":"124.04347527516074","resolution":{"w":"1366","h":"768"},"availableResolution":{"w":"728","h":"1366"},"ts":{"serve":1628709339039,"render":1628709338648}}',
        'specId': 'yidreg',
        'crumb': 'H4.yvLRdejE',
        'acrumb': '9Ach1eVW',
        'done': 'https://api.login.aol.com/oauth2/authorize?client_id=dj0yJmk9ZXRrOURhMkt6bkl5JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWQ2&intl=us&nonce=kYrCBuoE3NhBcpMPi7iWi4QTnplDEgs0&redirect_uri=https%3A%2F%2Foidc.www.aol.com%2Fcallback&response_type=code&scope=mail-r+openid+openid2+sdps-r&src=fp-us&state=eyJhbGciOiJSUzI1NiIsImtpZCI6IjZmZjk0Y2RhZDExZTdjM2FjMDhkYzllYzNjNDQ4NDRiODdlMzY0ZjcifQ.eyJyZWRpcmVjdFVyaSI6Imh0dHBzOi8vd3d3LmFvbC5jb20vIn0.hlDqNBD0JrMZmY2k9lEi6-BfRidXnogtJt8aI-q2FdbvKg9c9EhckG0QVK5frTlhV8HY7Mato7D3ek-Nt078Z_i9Ug0gn53H3vkBoYG-J-SMqJt5MzG34rxdOa92nZlQ7nKaNrAI7K9s72YQchPBn433vFbOGBCkU_ZC_4NXa9E',
        'attrSetIndex': '0',
        'tos0': 'oath_freereg|us|en-US',
        'firstName': 'dlsdl',
        'lastName': 'alo',
        'yid': str(eml),
        'password': 'https://t.me/SidraTools',
        'shortCountryCode': 'US',
        'phone': '2097635173',
        'mm': '1',
        'dd': '5',
        'yyyy': '2000',
        'freeformGender': '',
        'signup': '' }
        
		response = requests.request("POST", 'https://login.aol.com/account/module/create?validateField=yid', data=data, headers=headers)
		if str('"yid"') in str(response.text):
			massage = {'status':'null[]null','Telegram':'@SidraELEzz'}
			return massage
			
		else:
			massage = {'status':'Successful','Telegram':'@SidraELEzz'}
			return massage
			
	def Mailru(email: str) -> str:
		
		response = requests.request("POST", 'https://account.mail.ru/api/v1/user/exists', data= {'email': str(email)}, headers={'user-agent': str(generate_user_agent())})
		if str(response.json()['body']['exists']) == 'False':
			massage = {'status':'Successful','Telegram':'@SidraELEzz'}
			return massage
			
		else:
			massage = {'status':'null[]null','Telegram':'@SidraELEzz'}
			return massage
			
			
	def Instagram(email: str) -> str:
		headers={
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ar,en-US;q=0.9,en;q=0.8,ar-SA;q=0.7',
        'content-length': '61',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': 'ig_cb=2; ig_did=BB52B198-B05A-424E-BA07-B15F3D4C3893; mid=YAlcaQALAAHzmX6nvD8dWMRVYFCO; shbid=15012; rur=PRN; shbts=1612894029.7666144; csrftoken=CPKow8myeXW9AuB3Lny0wNxx0EzoDQoI',
        'origin': 'https://www.instagram.com',
        'referer': 'https://www.instagram.com/accounts/emailsignup/',
        'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': str(generate_user_agent()),
        'x-csrftoken': 'CPKow8myeXW9AuB3Lny0wNxx0EzoDQoI',
        'x-ig-app-id': '936619743392459',
        'x-ig-www-claim': 'hmac.AR0Plwj5om112fwzrrYnMNjMLPnyWfFFq1tG7MCcMv5_vN9M',
        'x-instagram-ajax': '72bda6b1d047',
        'x-requested-with': 'XMLHttpRequest'} 
        
		data={
        'email' :str(email),
        'username':str(email),
        'first_name': '@SidraELEzz',
        'opt_into_one_tap': 'false'}
        
		try:
			response = requests.request("POST", 'https://www.instagram.com/accounts/web_create_ajax/attempt/', data=data, headers=headers)
			successful = (response.json()["errors"]["email"])	       	
			massage = {'status':'Successful','Telegram':'@SidraELEzz'}
			return massage 
			
		except:
			massage = {'status':'null[]null','Telegram':'@SidraELEzz'}
			return massage 
			
	
				
				
				
				
	def Services():
		version = '136.0.0.34.124'
		varsion = '208061712'
		devices = {
		'one_plus_7': {'app_version': version,'android_version': '29','android_release': '10.0','dpi': '420dpi','resolution': '1080x2340','manufacturer': 'OnePlus','device': 'GM1903','model': 'OnePlus7','cpu': 'qcom','version_code': varsion},
		'one_plus_3': {'app_version': version,'android_version': '28','android_release': '9.0','dpi': '420dpi','resolution': '1080x1920','manufacturer': 'OnePlus','device': 'ONEPLUS A3003','model': 'OnePlus3','cpu': 'qcom','version_code': varsion},
		'samsung_galaxy_s7': {'app_version': version,'android_version': '26','android_release': '8.0','dpi': '640dpi','resolution': '1440x2560','manufacturer': 'samsung','device': 'SM-G930F','model': 'herolte','cpu': 'samsungexynos8890','version_code': varsion},
		'huawei_mate_9_pro': {'app_version': version,'android_version': '24','android_release': '7.0','dpi': '640dpi','resolution': '1440x2560','manufacturer': 'HUAWEI','device': 'LON-L29','model': 'HWLON','cpu': 'hi3660','version_code': varsion},
		'samsung_galaxy_s9_plus': {'app_version': version,'android_version': '28','android_release': '9.0','dpi': '640dpi','resolution': '1440x2560','manufacturer': 'samsung','device': 'SM-G965F','model': 'star2qltecs','cpu': 'samsungexynos9810','version_code': varsion},
		'one_plus_3t': {'app_version': version,'android_version': '26','android_release': '8.0','dpi': '380dpi','resolution': '1080x1920','manufacturer': 'OnePlus','device': 'ONEPLUS A3010','model': 'OnePlus3T','cpu': 'qcom','version_code': varsion},
		'lg_g5': {'app_version': version,'android_version': '23','android_release': '6.0.1','dpi': '640dpi','resolution': '1440x2392','manufacturer': 'LGE/lge','device': 'RS988','model': 'h1','cpu': 'h1','version_code': varsion},
		'zte_axon_7': {'app_version': version,'android_version': '23','android_release': '6.0.1','dpi': '640dpi','resolution': '1440x2560','manufacturer': 'ZTE','device': 'ZTE A2017U','model': 'ailsa_ii','cpu': 'qcom','version_code': varsion},
		'samsung_galaxy_s7_edge': {'app_version': version,'android_version': '23','android_release': '6.0.1','dpi': '640dpi','resolution': '1440x2560','manufacturer': 'samsung','device': 'SM-G935','model': 'hero2lte','cpu': 'samsungexynos8890','version_code': varsion},}
		davices  = random.choice(list(devices.keys()))
		versions = devices[davices]['app_version']
		androids = devices[davices]['android_version']
		endroids = devices[davices]['android_release']
		phonas   = devices[davices]['dpi']
		phones   = devices[davices]['resolution']
		manufa   = devices[davices]['manufacturer']
		devicees = devices[davices]['device']
		modelas = devices[davices]['model']
		apicup    = devices[davices]['cpu']
		versiones = devices[davices]['version_code']
		massage   =  'Instagram {} Android ({}/{}; {}; {}; {}; {}; {}; {}; en_US; {})'.format(str(versions),str(androids),str(endroids),str(phonas),str(phones),str(manufa),str(devicees),str(modelas),str(apicup),str(versiones))
		return massage
		
		
	
	
class Login:
	
	def __init__(self,username,password):
		self.username=username
		self.password=password
		m = hashlib.md5()
		m.update(username.encode('utf-8') + password.encode('utf-8'))
		self.device_id = self.Sidra(m.hexdigest())
		self.uuid = self.Sidraa(True)
		self.s = requests.Session()
		
		

	def Sidra(self, seed):
		volatile_seed = "12345"
		m = hashlib.md5()
		m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
		return 'android-' + m.hexdigest()[:16]

	def Sidraa(self, type):
		uuid_api = str(uuid.uuid4())
		if (type):
			return uuid_api
		else:
			return uuid_api.replace('-', '')

	
	def LoginAPI(self):
		token=self.s.get("https://www.instagram.com/",headers={"user-agent":str(generate_user_agent())}).text
		crf_token=re.findall(r"\"csrf_token\"\:\"(.*?)\"", str(token))[0]
		self.s.headers.update({
        'Connection': 'close',
	    'Accept': '*/*',
		'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'Cookie2': '$Version=1',
		'Accept-Language': 'en-US',
		'User-Agent': str(Hunter.Services())})
		self.data = json.dumps({
		'phone_id': self.Sidraa(True),
		'_csrftoken': crf_token,
		'username': self.username,
		'guid': self.uuid,
		'device_id': self.device_id,
		'password': self.password,
		'login_attempt_count': '0'})
		self.payload = 'signed_body={}.{}&ig_sig_key_version=4'.format(self.Sidraa(False),urllib.request.quote(self.data))
		respons = self.s.post("https://i.instagram.com/api/v1/accounts/login/", self.payload)
		response =json.loads(respons.text)
		cookie = respons.cookies.get_dict()
		if ("logged_in_user") in str(respons.text):
			cookies = ";".join([v+"="+cookie[v] for v in cookie])
			sessionid = str(self.s.cookies['sessionid'])
			userid = str(response['logged_in_user']['pk'])
			massage = {'status':'Successful','pk':str(userid),'sessionid':str(sessionid),'cookies':str(cookies),'Telegram':'@SidraELEzz'}
			return massage
			
		elif ('challenge_required') in str(respons.text):
			massage = {'status':'Checkpoint','Telegram':'@SidraELEzz'}
			return massage
			
		else:
			massage = {'status':'error','Telegram':'@SidraELEzz'}
			return massage



class Email:
	def Business(pk: str, sessionid: str) -> str:
		headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
        'cookie': 'mid=YF55GAALAAF55lDR3NkHNG4S-vjw; ig_did=F3A1F3B5-01DB-457B-A6FA-6F83AD1717DE; ig_nrcb=1; shbid=13126; shbts=1616804137.1316793; rur=PRN; ig_direct_region_hint=ATN; csrftoken=ot7HDQ6ZX2EPbVQe1P9Nqvm1WmMkzKn2; ds_user_id=46165248972; sessionid='+str(sessionid),
        'origin': 'https://www.instagram.com',
        'referer': 'https://www.instagram.com/',
        'user-agent': str(Hunter.Services()),
        'x-ig-app-id': '936619743392459',
        'x-ig-www-claim': 'hmac.AR0EWvjix_XsqAIjAt7fjL3qLwQKCRTB8UMXTGL5j7pkgbG4'}
        
		response = requests.Session().get("https://i.instagram.com/api/v1/users/"+str(pk)+"/info/", data=False, headers=headers).json()
		if response['user']['is_business'] == True and str(response['user']['public_email']) != "":
			username = str(response['user']['username'])
			followers = str(response['user']['follower_count'])
			following = str(response['user']['following_count'])
			lok = requests.request("GET","https://o7aa.pythonanywhere.com/?id="+str(self.userid)).json()
			date = lok['data']
			email = str(response['user'].get('public_email'))
			massage = {"username": username, "followers": followers, "following": following,"date": date,"email": email,'Telegram':'@SidraELEzz'}
			return massage
			
		else:
			massage = {'status':'null[]null','Telegram':'@SidraELEzz'}
			return massage
			
			
	
	