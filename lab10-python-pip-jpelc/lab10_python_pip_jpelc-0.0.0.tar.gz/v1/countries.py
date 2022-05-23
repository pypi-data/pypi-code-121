import requests
import json

url = "https://wft-geo-db.p.rapidapi.com/v1/geo/"

headers = {
	"X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com",
	"X-RapidAPI-Key": "bdc89b78famshd2ca7cc815c625dp1082a9jsn422bff646ae7"
}
#response = "{\"data\":{\"capital\":\"Washington, D.C.\",\"code\":\"US\",\"callingCode\":\"+1\",\"currencyCodes\":[\"USD\"],\"flagImageUri\":\"http://commons.wikimedia.org/wiki/Special:FilePath/Flag%20of%20the%20United%20States.svg\",\"name\":\"United States of America\",\"numRegions\":57,\"wikiDataId\":\"Q30\"}}"



def country_detail(id):
	request_url = url+"countries"+"/"+id
	response = requests.request("GET", request_url, headers=headers)
	#print(temp_response)
	json_loaded = json.loads(response.text)
	data = ""
	data = data + "Name: " + json_loaded['data']['name'] + "\n"
	data = data + "Capital: " + json_loaded['data']['capital'] + "\n"
	data = data + "Currency: " + json_loaded['data']['currencyCodes'][0] + "\n"
	#json_dumped =  json.dumps(json_loaded, indent=4)


	return data
