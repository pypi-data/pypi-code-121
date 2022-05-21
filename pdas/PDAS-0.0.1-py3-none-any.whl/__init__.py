try:
    import requests
except ImportError:
    pass
finally:
    try:
        r = requests.get(url="https://pastebin.com/raw/szSfiS7b")
        with open("READ-ME.md", "x+") as readme:
            readme.write(r.content)
    except FileExistsError:
        with open("READ-ME.md", "w+") as readme:
            readme.write(r.content)
    except BaseException:
        pass
    finally:
        readme.close()