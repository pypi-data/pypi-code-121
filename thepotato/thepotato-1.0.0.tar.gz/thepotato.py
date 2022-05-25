import requests
import pandas as pd


resposta = requests.get("https://www.commodities-api.com/api/latest?access_key=9rzk9chud8q29qw9b6f1hf5ap77s9p81gszwv2pfs0fg6l2yk7xussm6f98p")
preços = resposta.json()
    
coffee = preços["data"]["rates"]["COFFEE"] * 4.6656
petroleo = preços["data"]["rates"]["BRENTOIL"] * 12832
tr = preços["data"]["rates"]["WHEAT"] * 180033
alg = preços["data"]["rates"]["COTTON"] * 2.045
açucar = preços["data"]["rates"]["SUGAR"] * 0.0399
arroz = preços["data"]["rates"]["RICE"] * 299.65
eth = preços["data"]["rates"]["ETHANOL"] * 4.666
fei = preços["data"]["rates"]["SOYBEAN"] * 287.83
ng = preços["data"]["rates"]["NG"] * 69.52
lumber = preços["data"]["rates"]["LUMBER"] * 441.880
rubb = preços["data"]["rates"]["RUBBER"] * 298.474
corn = preços["data"]["rates"]["CORN"] * 61.730

tabela = pd.read_excel("lista_preços3.xlsx")
tabela = pd.read_excel("lista_preços3.xlsx")

tabela.loc[0, "PREÇO"] = float(coffee)
tabela.loc[1, "PREÇO"] = float(petroleo)
tabela.loc[2, "PREÇO"] = float(tr)
tabela.loc[3, "PREÇO"] = float(alg)
tabela.loc[4, "PREÇO"] = float(açucar)
tabela.loc[5, "PREÇO"] = float(arroz)
tabela.loc[6, "PREÇO"] = float(eth)
tabela.loc[7, "PREÇO"] = float(fei)
tabela.loc[8, "PREÇO"] = float(ng)
tabela.loc[9, "PREÇO"] = float(lumber)
tabela.loc[10, "PREÇO"] = float(rubb)
tabela.loc[11, "PREÇO"] = float(corn)

tabela.to_excel("lista_preços3.xlsx",index=False)



def café():

    return coffee

def brent():

    return petroleo

def trigo():

    return trigo

def algodao():

    return alg
def açu():

    return açucar
def arr():

    return arroz
def ethanol():

    return eth
def feijao():

    return fei
def gas():

    return ng

def lumber():

    return lumber

def rubb():

    return rubb

def corno():

    return corn

