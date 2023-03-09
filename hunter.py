from requests import get
from bs4 import BeautifulSoup
from pyrogram.types import InputMediaPhoto, InputMediaDocument, CallbackQuery
from pyrogram import Client
from buttons import getButtons

def getHunterBooks(searchterm):
    params = {
        'keyword': searchterm,
        'x': '0',
        'y': '0',
    }

    res = get('https://ebook-hunter.org/search', params=params)
    soups = BeautifulSoup(res.content, "html.parser")
    soups = soups.findAll("div", class_="index_box")
    books = []

    for soup in soups:
        aas = soup.findAll("a")
        info = soup.find("div",class_="index_box_info list_title").text.replace("\t","").replace("\r","").replace("\n","").replace(" ","").split("|")
        book = {
                "link" : "https://ebook-hunter.org" + aas[1].get("href"),
                "cover" : soup.find("img").get("src").replace("_small",""),
                "title" : aas[1].text.replace("\t","").replace("\r","").replace("\n",""),
                "extension" : info[0],
                "language" : info[1],
                "date" : info[2],
                "author" : info[3].replace("Author:","")
            }
        books.append(book)

    return books


def getDlink(book):
    res = get(book["link"])
    soup = BeautifulSoup(res.content,"html.parser")
    dlink = soup.find("div", class_="to-lock").find("a").get("href") + "/"
    return dlink


def getHuntText(books,choose=0):
    return f'**{books[choose]["title"]}**\n\n__Author: {books[choose]["author"]}\nDate: {books[choose]["date"]}\nLanguage: {books[choose]["language"]}\nExtension: {books[choose]["extension"]}__' + "\n\n------[Ebook Hunter]------"


def handleHunt(app:Client,call:CallbackQuery,books):

    # download
        if call.data[0] == "D":
            choose = int(call.data.replace("D",""))
            link = getDlink(books[choose])                
            app.edit_message_text(call.message.chat.id, call.message.id, f'**{books[choose]["title"]}**\n\n__External Link : {link}__')
            return

        #  next
        choose = int(call.data) % len(books)
        app.edit_message_media(call.message.chat.id, call.message.id,
            InputMediaPhoto(books[choose]["cover"],getHuntText(books,choose)),
            reply_markup=getButtons(choose))