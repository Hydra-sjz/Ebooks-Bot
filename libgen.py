from os import remove
from libgen_api import LibgenSearch
from requests import get
from bs4 import BeautifulSoup
from pyrogram.types import InputMediaPhoto, InputMediaDocument, CallbackQuery
from pyrogram import Client
from buttons import getButtons


LibGen = LibgenSearch()
noimage = "https://t3.ftcdn.net/jpg/04/34/72/82/360_F_434728286_OWQQvAFoXZLdGHlObozsolNeuSxhpr84.jpg"


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
    else: return noimage

def getBookImg(book):
    try:
        link = book["Mirror_1"]
        r = get(link)
        soup = BeautifulSoup(r.text,"html.parser")
        src = soup.find("img").get("src")
        return imgValid("https://libgen.rs" + src)
    except:
        return noimage

def getLibText(books,choose=0):
    return f'**{books[0]["Title"]}**\n\n__Author: {books[choose]["Author"]}\nPublisher: {books[choose]["Publisher"]}\nYear: {books[choose]["Year"]}\nSize: {books[choose]["Size"]}\nPages: {books[choose]["Pages"]}\nLanguage: {books[choose]["Language"]}\nExtension: {books[choose]["Extension"]}__' + "\n\n------[LibraryGenesis]------"

def handleLibGen(app:Client,call:CallbackQuery,books):

    # download
        if call.data[0] == "D":
            choose = int(call.data.replace("D",""))
            app.edit_message_text(call.message.chat.id, call.message.id, "__Downloading__")
            links = getDownLink(books[choose])

            i = 0
            while i<len(links):
                print(links[i])
                res = get(links[i])
                if res.status_code == 200: break
                else: i += 1
            
            if i == len(books):
                app.edit_message_text(call.message.chat.id, call.message.id, "__Failed__")
                return 

            filename = f"{books[choose]['Title']}"
            filename = "".join( x for x in filename if (x.isalnum() or x in "_ ")) + f".{books[choose]['Extension']}"
            with open(filename, "wb") as file:
                file.write(res.content)

            res = get(getBookImg(books[choose]))
            thumbfile = f"{books[choose]['Title']}"
            thumbfile = "".join( x for x in thumbfile if (x.isalnum() or x in "_ ")) + ".jpg"
            with open(thumbfile, "wb") as file:
                file.write(res.content)
                
            app.edit_message_text(call.message.chat.id, call.message.id, "__Uploading__")
            app.edit_message_media(call.message.chat.id, call.message.id, InputMediaDocument(filename, thumb=thumbfile, caption=f"**{books[choose]['Title']}**"))
            remove(filename)
            remove(thumbfile)
            return

        #  next
        choose = int(call.data) % len(books)
        app.edit_message_media(call.message.chat.id, call.message.id,
            InputMediaPhoto(getBookImg(books[choose]),getLibText(books,choose)),
            reply_markup=getButtons(choose))