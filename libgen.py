from libgen_api import LibgenSearch
LibGen = LibgenSearch()
from requests import get
from bs4 import BeautifulSoup

wrongimage = "https://w7.pngwing.com/pngs/389/161/png-transparent-sign-symbol-x-mark-check-mark-christian-cross-symbol-miscellaneous-angle-logo-thumbnail.png"

def getDownLink(book):
    res = LibGen.resolve_download_links(book)
    data = []
    for key in res: data.append(res[key])
    return data

def getBooks(name):
    return LibGen.search_title(name)

def imgValid(url):
    re = get(url)
    if re.status_code == 200: return url
    else: return wrongimage

def getBookImg(book):
    try:
        link = book["Mirror_1"]
        r = get(link)
        soup = BeautifulSoup(r.text,"html.parser")
        src = soup.find("img").get("src")
        return imgValid("https://libgen.rs" + src)
    except:
        return wrongimage
