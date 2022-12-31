from libgen_api import LibgenSearch
LibGen = LibgenSearch()
from requests import get
from bs4 import BeautifulSoup

def getDownLink(book):
    res = LibGen.resolve_download_links(book)
    data = []
    for key in res: data.append(res[key])
    return data

def getBooks(name):
    return LibGen.search_title(name)

def getBookImg(book):
    link = book["Mirror_1"]
    r = get(link)
    soup = BeautifulSoup(r.text,"html.parser")
    src = soup.find("img").get("src")
    return "https://libgen.rs" + src

