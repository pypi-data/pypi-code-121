import time
import requests
from bs4 import BeautifulSoup
import ray

@ray.remote
def et_fetch():
    session = requests.Session()
    data = session.get("https://economictimes.indiatimes.com/markets")
    soup = BeautifulSoup(data.content, "lxml")

    links = []
    titles = []
    descs = []
    imgs = []

    a_data = soup.find(id = "topStories")
    a_tags = a_data.find_all("a")
    count = 0
    for a in a_tags:
        count += 1
        if a["href"][:21] == "/markets/stocks/news/":
            links.append(f'https://economictimes.indiatimes.com{a["href"]}')
            titles.append(a.text)
        if count == 5:
            break
    
    for index, link in enumerate(links):
        article = session.get(link)
        article_soup = BeautifulSoup(article.content, "lxml")

        try:
            desc = article_soup.find_all("h2", attrs = {"class", "summary"})[0].text
            descs.append(desc)

            img = article_soup.find_all("img")
            imgs.append(img[3]["src"])
        except:
            links.remove(link)
            titles.pop(index)
        time.sleep(0.01)

    data = []
    for index, link in enumerate(links):
        data.append({
            "title": titles[index],
            "desc": descs[index],
            "link": link,
            "img": imgs[index]
        })
    
    if len(data) > 5:
        data = data[:5]
    
    return data