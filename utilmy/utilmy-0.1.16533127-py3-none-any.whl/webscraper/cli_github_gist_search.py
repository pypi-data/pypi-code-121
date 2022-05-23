# About: Search & Scrape GitHub repositories
"""Search on github for keyword(s) with optional parameters to refine your search and get all results in a CSV file.
Doc::

    pip install -e .
    $utilmy = "yourfolder/myutil/utilmy/
    python  $utilmy/webscraper/cli_github_gist_search.py  run --url "https://gist.github.com/search?p={}&q=pyspark+UDF"    --dirout "./zdown/"



"""
import requests, csv, os, zipfile
from io import BytesIO
from bs4 import BeautifulSoup as bs


def run(url= "https://gist.github.com/search?p={}&q=pyspark+UDF"  , logs=True, download=True, dirout="./zdown_github/"):
    try:
        os.makedirs(dirout, exist_ok=True)
        dwnldDir = dirout
        os.makedirs(os.path.join(dwnldDir,  "github_files"), exist_ok=True)
        csvFilePath = os.path.join(dwnldDir, "GitHub_files.csv")
        with open(csvFilePath, 'w') as f:
            w = csv.writer(f)
            w.writerow(["filename", "file_url", "url_full"])
        u = url
        filesList = []
        for i in range(1, 53):
            url = u.format(i)
            if logs:
                print("=="*20)
                print(i, url)    
            data = requests.get(url)
            obj = bs(data.text, 'html.parser')
            files = obj.findAll('a', {'class': "link-overlay"})
            for f in files:
                try:
                    fName = f.find('span').find('strong').text
                    fUrl = f['href']
                    data = requests.get(fUrl)
                    obj = bs(data.text, 'html.parser')
                    fileDir = os.path.join(dwnldDir, "github_files", fName.split('.')[0])
                    fileDwnldUrl = "https://gist.github.com" + obj.findAll('a', {'data-ga-click': "Gist, download zip, location:gist overview"})[0]['href']
                    if download:
                        data = requests.get(fileDwnldUrl)
                        zip_file = zipfile.ZipFile(BytesIO(data.content))
                        zip_file.extractall(fileDir)
                    with open(csvFilePath, 'a', newline='') as f:
                        w = csv.writer(f)
                        w.writerow([fName, fUrl, fileDwnldUrl])
                    if logs:
                        print("\t", fName)
                        print("\t", "\t", fUrl)
                        print("\t", "\t", fileDwnldUrl)
                except Exception as e:
                    print(e)
            if logs:
                print("=="*20)
            else:
                print("InProgress...")
        print("Done")
    except Exception as e:
        print(e)



if __name__ == "__main__":
    import fire 
    fire.Fire()
    #### python  utilmy$/webscraper/cli_github_gist_search.py  run
