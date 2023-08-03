# from openlibrary.setup.loginAccount import loginAndGetKey
from openlibrary.setup.fulfill import downloadFile

from openlibrary.decrypt.decodePDF import decryptPDF
from openlibrary.decrypt.decodeEPUB import decryptEPUB

# import argparse
from os import mkdir, remove, rename
from os.path import exists

from openlibrary.setup.params import FILE_DEVICEKEY, FILE_DEVICEXML, FILE_ACTIVATIONXML
from openlibrary.decrypt.params import KEYPATH
from openlibrary.setup.data import createDefaultFiles
from openlibrary.setup.ia import SESSION_FILE, manage_login, get_book, return_book

from requests import get
from bs4 import BeautifulSoup
from pyrogram.types import InputMediaPhoto, InputMediaDocument, CallbackQuery
from pyrogram import Client
from buttons import getButtonsIA
from os import remove

# def loginADE(email, password):
#     if email is None or password is None:
#         # print("Email or Password cannot be empty")
#         # print()
#         return
#     if not exists('account'): mkdir('account')
#     loginAndGetKey(email, password)
#     # print()

def loginIA(email,password):
    if email is None or password is None:
        # print("Email or Password cannot be empty")
        # print()
        return
    return manage_login(email,password)
    # print()

def acsm(acsmFile, outputFilename):
    if not exists('account'): mkdir('account')

    # setting up the account and keys
    if not (exists(FILE_ACTIVATIONXML) and exists(FILE_DEVICEXML) and exists(FILE_DEVICEKEY) and exists(KEYPATH)):
        createDefaultFiles()
    # print()

    # cheek for file existance
    if not exists(acsmFile):
        # print(f"{acsmFile} file does not exist")
        # print()
        return

    # download
    encryptedFile = downloadFile(acsmFile)
    # print(encryptedFile)
    # print()
    if encryptedFile is None: return None

    # decrypt
    if encryptedFile.endswith(".pdf"):
        decryptedFile = decryptPDF(encryptedFile)
    elif encryptedFile.endswith(".epub"):
        decryptedFile = decryptEPUB(encryptedFile)
    else:
        # print("File format not supported")
        # print()
        return

    remove(encryptedFile)
    if outputFilename is None:
        tempName = encryptedFile
    else:
        tempName = outputFilename
    rename(decryptedFile, tempName)
    # print(tempName)
    # print()
    return tempName

def handle_IA(url,format="pdf"):
    if not exists(SESSION_FILE):
        print("Login to InternetArchive first or give ACSM file as input")
        return
    acsmFile = get_book(url,format)
    if acsmFile is None:
        print("Could not get Book, try using ACSM file as input")
        return
    ofile = acsm(acsmFile,None)
    remove(acsmFile)
    if(return_book(url) is None):
        # print("Please return it yourself")
        pass
    return ofile


def getOpenlibbooks(search):
    headers = {
        'authority': 'openlibrary.org',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://openlibrary.org/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }

    params = {
        'q': search,
        'mode': 'everything',
    }

    response = get('https://openlibrary.org/search', params=params, headers=headers)
    soups = BeautifulSoup(response.text, "html.parser").findAll("li", class_="searchResultItem")
    books = []

    for soup in soups:
        if (soup.find("div", class_="cta-button-group").find("a", class_="cta-btn cta-btn--missing")): continue

        if soup.find("img").get("src") == "/images/icons/avatar_book-sm.png": cover = "https://openlibrary.org//images/icons/avatar_book-sm.png"
        else: cover = "https:" + soup.find("img").get("src")

        try: ia = [x.get("href").split("ia:")[-1] for x in soup.find("span", class_="preview-covers").findAll("a")]
        except: ia = soup.find("div", class_="cta-button-group").find('a').get("href").split("/")[-1].split("?")[0]

        book = {
            "title": soup.find("h3").text.replace("\n",""),
            "author": soup.find("span", itemprop="author").text.split("by ")[-1].replace("\n",""),
            "year": soup.find("span", class_="publishedYear").text.split("First published in ")[-1].replace("\n","").replace(" ",""),
            "cover": cover,
            "ia" : ia,
        }
        books.append(book)
    
    return books

def getOpenText(books,choose=0,final=False):
    if isinstance(books[choose]['ia'], list):
        listt = "\n"
        for i in range(len(books[choose]["ia"])):
            listt += f'{i+1}. https://archive.org/details/{books[choose]["ia"][i]}\n'
    else: listt = "https://archive.org/details/" + books[choose]["ia"] + "\n"

    txt = f'**{books[choose]["title"]}**\n\n__Author: {books[choose]["author"]}\nYear: {books[choose]["year"]}\n\nEdition/s: {listt}__' + "\n------[Open Library]------"
    if not final: txt += f"  [{choose+1}/{len(books)}]"
    return txt


def handleOpen(iaemail, iapass, app:Client,call:CallbackQuery,books):

    # download
        if call.data[0] == "D":

            choose = int(call.data.replace("D","").split(",")[0])
            if isinstance(books[choose]['ia'], str): suffix = books[choose]["ia"]
            else: suffix = books[choose]["ia"][int(call.data.replace("D","").split(",")[1])]
            app.edit_message_text(call.message.chat.id, call.message.id, "__Trying to Download without Loan__")
            nor = get(f"https://archive.org/download/{suffix}/{suffix}.pdf")
            
            if nor.status_code != 200:
                IA = False if not (iaemail and iapass) else loginIA(iaemail, iapass)
                if not IA:
                    app.edit_message_text(call.message.chat.id, call.message.id,"__Empty/Wrong Crenditals for IA, you can't Download__")
                    return
                app.edit_message_text(call.message.chat.id, call.message.id, "__Downloading__")
                link = "https://archive.org/details/" + suffix
                filename = handle_IA(link)
            else:
                filename = "".join( x for x in books[choose]['title'] if (x.isalnum() or x in "_ ")) + ".pdf"
                with open(filename, "wb") as file:
                    file.write(nor.content)

            if filename is None:
                app.edit_message_text(call.message.chat.id, call.message.id,"__Failed, problem in Downloading/Decrypting__")
                return

            res = get(books[choose]["cover"])
            thumbfile = "".join( x for x in books[choose]['title'] if (x.isalnum() or x in "_ ")) + ".jpg"
            with open(thumbfile, "wb") as file:
                file.write(res.content)
                
            app.edit_message_text(call.message.chat.id, call.message.id, "__Uploading__")
            app.edit_message_media(call.message.chat.id, call.message.id, InputMediaDocument(filename, thumb=thumbfile, caption=getOpenText(books,choose,True)))
            remove(filename)
            remove(thumbfile)
            return True

        #  next
        choose = int(call.data) % len(books)
        app.edit_message_media(call.message.chat.id, call.message.id,
            InputMediaPhoto(books[choose]["cover"],getOpenText(books,choose)),
            reply_markup=getButtonsIA(books,choose))
        return False
