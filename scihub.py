import requests
from bs4 import BeautifulSoup
from scholarly import scholarly
from os import remove
from pyrogram.types import InputMediaPhoto, InputMediaDocument, CallbackQuery
from pyrogram import Client
from buttons import getButtons

SCIHUB_URL = 'https://sci-hub.se/'
PROXY = True
noimage = "https://t3.ftcdn.net/jpg/04/34/72/82/360_F_434728286_OWQQvAFoXZLdGHlObozsolNeuSxhpr84.jpg"

if PROXY:
    from scholarly import ProxyGenerator
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)


def getSciPubs(search):
    results = []
    res = scholarly.search_pubs(search, citations=False, patents=False)
    for _ in range(10):
        pub = {}
        try:
            tmp = next(res)
            pub["url"] = tmp["pub_url"]
            for tt in tmp["bib"]: pub[tt] = tmp["bib"][tt]
            pub["author"] = ", ".join(pub["author"])
            if len(pub["abstract"]) > 500: pub["abstract"] = pub["abstract"][:500] + "..."
            results.append(pub)
        except: break
    return results


def is_pdf(url):
    try:
        response = requests.get(url)
        if (url.endswith('.pdf')) or ('Content-Type' in response.headers and 
            'application/pdf' in response.headers['Content-Type']): return response.content
    
        content_start = response.raw.read(5)
        if content_start.startswith(b'%PDF-'): return response.content
        return False
    except requests.exceptions.RequestException: return False


def downloadSci(book):
    url = book["url"]
    tmp = is_pdf(url)
    if tmp: return tmp

    headers = {
        'Referer': SCIHUB_URL,
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    response = requests.get(f'{SCIHUB_URL}{url}', headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    try: durl = SCIHUB_URL[:-1] + soup.find("div", id="article").find('embed').get('src')
    except: return False

    return is_pdf(durl)


def getSciText(books,choose=0,final=False):
    txt = f'**{books[choose]["title"]}**\n\n__Author: {books[choose]["author"]}\nVenue: {books[choose]["venue"]}\nYear: {books[choose]["pub_year"]}\nAbstract: {books[choose]["abstract"]}__' \
    + "\n\n------[SciHub]------"
    if not final: txt += f"  [{choose+1}/{len(books)}]"
    return txt


def handleSchiHub(app:Client,call:CallbackQuery,books):

    # download
        if call.data[0] == "D":
            choose = int(call.data.replace("D",""))
            app.edit_message_text(call.message.chat.id, call.message.id, "__Downloading__")
            content = downloadSci(books[choose])
            
            if not content:
                app.edit_message_text(call.message.chat.id, call.message.id, "__Not Available__")
                return True

            filename = f"{books[choose]['title']}"
            filename = "".join( x for x in filename if (x.isalnum() or x in "_ ")) + ".pdf"
            with open(filename, "wb") as file:
                file.write(content)
                
            app.edit_message_text(call.message.chat.id, call.message.id, "__Uploading__")
            app.edit_message_media(call.message.chat.id, call.message.id, InputMediaDocument(filename, caption=getSciText(books,choose,True)))
            remove(filename)
            return True

        #  next
        choose = int(call.data) % len(books)
        try:
            app.edit_message_media(call.message.chat.id, call.message.id,
                InputMediaPhoto(books[choose]["url"]),getSciText(books,choose),
                reply_markup=getButtons(choose))
        except: 
            app.edit_message_media(call.message.chat.id, call.message.id,
                InputMediaPhoto(noimage),getSciText(books,choose),
                reply_markup=getButtons(choose))
        return False