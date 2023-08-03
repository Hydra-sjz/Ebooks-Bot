from os import remove
from requests import get
# from bs4 import BeautifulSoup
from pyrogram.types import InputMediaPhoto, CallbackQuery # ,InputMediaDocument
from pyrogram import Client
from buttons import getButtons, getExtButton

wrongimage = "https://i.ibb.co/9pBPB5S/wrong.png"

def getpage(searchterm):

    cookies = {
        'access': '',
    }

    headers = {
        'authority': 'pdfdrive.to',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'referer': 'https://pdfdrive.to/top-python-books',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }

    params = {
        'slug': searchterm,
    }

    response = get(
        'https://pdfdrive.to/_next/data/WLYnM8yWFbxvIbU-Gz9lZ/search-tag.json',
        params=params,
        cookies=cookies,
        headers=headers,
    ).json()
    
    books = []
    for ele in response["pageProps"]["data"]["results"]:
        if not ele["status"]: continue
        book = {}
        book["id"] = ele["id"]
        book["link"] = "https://pdfdrive.to/filedownload/" + ele["slug"]
        book["coverlink"] = ele.get("thumbnail",wrongimage)
        book["title"] = ele["name"]
        book["author"] = str(ele.get("author","")).replace("\n"," ")
        book["pages"] = str(ele["page"])
        book["year"] = str(ele["release_year"])
        book["size"] = str(ele["file_size"]) + "MB"
        book["downloads"] = book["link"]
        book["lang"] = ele["language"]
        books.append(book)

    return books


def getPdfText(books,choose=0):
    return f'**{books[choose]["title"]}**\n\n__Year: {books[choose]["year"]}\nSize: {books[choose]["size"]}\nPages: {books[choose]["pages"]}\nAuthor: {books[choose]["author"]}\nLanguage: {books[choose]["lang"]}__' \
    + "\n\n------[PDFdrive]------" + f"  [{choose+1}/{len(books)}]"


def handlePdfdrive(app:Client,call:CallbackQuery,books:list):

    # download
        if call.data[0] == "D":
            choose = int(call.data.replace("D",""))
            app.edit_message_reply_markup(call.message.chat.id, call.message.id,
                    getExtButton(books[choose]["downloads"]))
            return True
            
        #  next
        choose = int(call.data) % len(books)
        templst = [books[choose]["coverlink"],books[choose]["link"],wrongimage]
        for ele in templst:
            try:
                app.edit_message_media(call.message.chat.id, call.message.id,
                InputMediaPhoto(ele,getPdfText(books,choose)),
                reply_markup=getButtons(choose))
                break
            except: pass
        return False
