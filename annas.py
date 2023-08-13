from requests import get
from bs4 import BeautifulSoup
from pyrogram.types import InputMediaPhoto, InputMediaDocument, CallbackQuery
from pyrogram import Client
from buttons import getButtons
from os import remove

DOMAIN = "https://annas-archive.gs"

def getAnnasBooks(searchbook):
    params = {'q': searchbook}
    response = get(f"{DOMAIN}/search", params=params)
    soups = BeautifulSoup(response.content,"html.parser")
    try:soups = soups.findAll("div",class_="h-[125]")
    except: return None
    books = []

    for soup in soups:
        soup = BeautifulSoup(str(soup).replace("<!--","").replace("-->",""),"html.parser")
        info = soup.find("div",class_="relative top-[-1] pl-4 grow overflow-hidden")
        desc = info.find("div",class_="truncate text-xs text-gray-500").text.split(",")

        book = {}
        try: book["link"] = DOMAIN + soup.find("a").get("href")
        except: pass
        try: book["cover"] = soup.find("img").get("src")
        except: pass
        try: book["title"] =  info.find("h3",class_="truncate text-xl font-bold").text
        except: book["title"] = "annas"
        try: book["publisher"] = info.find("div",class_="truncate text-sm").text
        except: pass
        try: book["author"] = info.find("div",class_="truncate italic").text
        except: pass
        try: book["language"] = desc[0]
        except: pass
        try: book["extension"] = desc[1][1:]
        except: pass
        try: book["size"] = desc[2][1:]
        except: pass
        try: book["filename"] = desc[3].replace('"',"")[1:]
        except: pass

        books.append(book)

    return books


def resolve_lib_download_links(url):
        page = get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.find_all("a", string=["GET", "Cloudflare", "IPFS.io", "Infura"])
        download_links = ["https://" + url.split("/")[2] + "/" + link["href"] for link in links]
        return download_links


def getDownLinks(book):
    headers = {
        'authority': 'annas-archive.org',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }

    res = get(book["link"])
    soup = BeautifulSoup(res.content,"html.parser")
    soup = soup.find("div",class_="mb-6").findAll("a")
    links = []
    for ele in soup:
        link = ele.get("href")
        if "/slow_download" == link[:len("/slow_download")]:
            url = DOMAIN + link
            res = get(url,headers=headers)
            soup = BeautifulSoup(res.content,"html.parser")
            try: links.append(soup.find("p",class_="mb-4").find("a").get("href"))
            except: links.append(url)
        elif "http://lib" == link[:len("http://lib")]:
            tmp = resolve_lib_download_links(link)
            for li in tmp: links.insert(0,li)
        elif "https://" == link[:len("https://")]: links.insert(0,link)
    return links


def getAnnasText(books,choose=0,final=False):
    text = ""
    try: text += f'**{books[choose]["title"]}**\n\n'
    except: pass
    try: text += f'__Author: {books[choose]["author"]}\n'
    except: text += '__'
    try: text += f'Publisher: {books[choose]["publisher"]}\n'
    except: pass
    try: text += f'Size: {books[choose]["size"]}\n'
    except: pass
    try: text += f'Language: {books[choose]["language"]}\n'
    except: pass
    try: text += f'Extension: {books[choose]["extension"]}__'
    except: text += '__'
    text += "\n\n------[Annas Archive]------"
    if not final: text += f"  [{choose+1}/{len(books)}]"
    return text
 


def handleAnnas(app:Client,call:CallbackQuery,books):

    # download
        if call.data[0] == "D":
            choose = int(call.data.replace("D",""))
            app.edit_message_text(call.message.chat.id, call.message.id, "__Downloading__")
            links = getDownLinks(books[choose])

            for link in links:
                print(link)
                res = get(link)
                if res.status_code == 200: break
            else: 
                app.edit_message_text(call.message.chat.id, call.message.id, "__Failed__")
                return True

            filename = f"{books[choose]['title']}"
            filename = "".join( x for x in filename if (x.isalnum() or x in "_ ")) + f".{books[choose]['extension']}"
            with open(filename, "wb") as file:
                file.write(res.content)

            res = get(books[choose]["cover"])
            thumbfile = f"{books[choose]['title']}"
            thumbfile = "".join( x for x in thumbfile if (x.isalnum() or x in "_ ")) + ".jpg"
            with open(thumbfile, "wb") as file:
                file.write(res.content)
                
            app.edit_message_text(call.message.chat.id, call.message.id, "__Uploading__")
            app.edit_message_media(call.message.chat.id, call.message.id, InputMediaDocument(filename, thumb=thumbfile, caption=getAnnasText(books,choose, True)))
            remove(filename)
            remove(thumbfile)
            return True

        #  next
        choose = int(call.data) % len(books)
        app.edit_message_media(call.message.chat.id, call.message.id,
            InputMediaPhoto(books[choose]["cover"],getAnnasText(books,choose)),
            reply_markup=getButtons(choose))
        return False
