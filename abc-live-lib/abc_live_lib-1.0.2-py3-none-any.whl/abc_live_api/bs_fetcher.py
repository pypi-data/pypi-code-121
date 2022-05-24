import time
import requests
from bs4 import BeautifulSoup
import ray

@ray.remote
def bs_fetch():
    session = requests.Session()
    data = session.get("https://www.business-standard.com/")
    soup = BeautifulSoup(data.content, "html.parser")

    links = []
    titles = []
    descs = []
    imgs = []

    a_data = soup.find(class_ = "row-inner topB")
    a_tags = a_data.find_all("a")
    topics = ["economy-policy", "companies"]
    for a in a_tags:
        try:
            topic = a["href"].split("/")[2]
        except:
            continue

        if a["href"][:9] == "/article/" and a["href"][-5:] == ".html" and topic in topics:
            links.append(f'https://www.business-standard.com{a["href"]}')
            titles.append(a.text)

    for index, link in enumerate(links):
        if titles[index] == "\n\n":
            links.remove(link)
            titles.pop(index)
            continue
    
    for index, link in enumerate(links):
        article = session.get(link)
        article_soup = BeautifulSoup(article.content, "html.parser")

        try:
            desc = article_soup.find("h2", attrs = {"class", "alternativeHeadline"}).text
            descs.append(desc)

            img = article_soup.find("img", attrs = {"class", "imgCont"})
            if not img:
                imgs.append(None)
                continue
            imgs.append(img["src"])
        except:
            try:
                links.remove(link)
                titles.pop(index)
            except:
                continue
        time.sleep(0.01)

    data = []
    for index, link in enumerate(links):
        data.append({
            "title": titles[index],
            "desc": descs[index],
            "link": links[index],
            "img": imgs[index]
        })

    for i in data:
        if not i["img"]:
            data.remove(i)

    if len(data) > 5:
        data = data[:5]

    return data