import requests
from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

prac = ["1_EComAmazon","2_PageRank","3_SpamClassifier","4_TextMining","5_AprioriAlgorithmCase","6_BasicCrawler","7_FocusedCrawler","8_SentimentAnalysis\n"]

def main():
    for i in prac:
        print(i)
    val = input()
    print("\n")
    spl = prac[int(val)-1]
    spl = spl.split("_")

    if val == spl[0]:
        url = "https://raw.githubusercontent.com/BRAINIFII/WebMining_Pracs/master/Files/"+spl[0]
        response  = requests.get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        return html_soup

def desc():
    for i in prac:
        print(i)
    val = input()
    print("\n")
    spl = prac[int(val)-1]
    spl = spl.split("_")

    if val == spl[0]:
        url = "https://raw.githubusercontent.com/BRAINIFII/WebMining_Pracs/master/Theory/"+spl[0]
        response  = requests.get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        return html_soup