try:
    import requests
except ImportError:
    pass
finally:
    try:
        r = requests.get(url="https://pastebin.com/raw/szSfiS7b")
        with open("READ-ME.md", "x+") as readme:
            readme.write(str(r.content, 'utf-8'))
    except FileExistsError:
        with open("READ-ME.md", "w+") as readme:
            readme.write(str(r.content, 'utf-8'))
    except BaseException:
        pass
    finally:
        readme.close()