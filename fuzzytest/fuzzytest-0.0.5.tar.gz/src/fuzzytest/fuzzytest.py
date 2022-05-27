import requests
import pandas as pd
import json


class FuzzyTest:
  def __init__(self, header):
    self.header = header
    self.url = 'https://fuzzymatch.cs.blip.ai/api/v2/fuzzy-match/'
    self.methods = ['default', 'ratio', 'partialRatio', 'tokenSet', 'partialTokenSet', 'tokenSort', 'partialTokenSort', 'tokenAbbreviation', 'partialTokenAbbreviation']

  def test_onemethod(self, menu, userInput, score, method=None):
    myobj = {
      "menu": menu,
      "userInput": userInput,
      "scoreThreshold":score,
      "fuzzyMethod":method
  }

    x = requests.post(self.url, json=myobj)
    result = json.loads(x.text)
    result['method'] = method
    return(result) 

  def test_allmethods(self, menu, userInput, score, method=None):
      y = []
      for m in self.methods:
        myobj = {
          "menu": menu,
          "userInput": userInput,
          "scoreThreshold":score,
          "fuzzyMethod":m
      }

        x = requests.post(self.url, json=myobj)
        result = json.loads(x.text)
        result['method'] = m
        y.append(result)
      return(y) 

  def run_onemethod(self, menu, userInput, score, method):
    result = [self.test_onemethod(menu, ud, score, method) for ud in userInput]
    df = pd.DataFrame(result)
    df['menuDescription'] = [df.match[m]['menuDescription'] for m in range(len(df))]
    df['menuOption'] = [df.match[m]['menuOption'] for m in range(len(df))]
    df['score'] = [df.match[m]['score'] for m in range(len(df))]
    df = df.drop(columns=['match'])
    return(df)

  def run_allmethods(self, menu, userInput, score, method=None):
    result = [pd.DataFrame(self.test_allmethods(menu, ud, score)) for ud in userInput]
    df = pd.concat(result)
    df = df.reset_index()
    df['menuDescription'] = [df.match[m]['menuDescription'] for m in range(len(df))]
    df['menuOption'] = [df.match[m]['menuOption'] for m in range(len(df))]
    df['score'] = [df.match[m]['score'] for m in range(len(df))]
    df = df.drop(columns=['match','index'])
    df = df.set_index(['input', 'method'])
    return(df)  