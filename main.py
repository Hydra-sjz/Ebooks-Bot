import os
import pyrogram
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton, InputMediaPhoto, InputMediaDocument
import getbooks
import requests

bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)


data = []
class save:
    msgid: str
    books: list

def storedata(msgid,books):
    new = save()
    new.msgid = msgid
    new.books = books
    data.append(new)

def getdata(msgid):
    for ele in data:
        if ele.msgid == msgid:
            return ele.books
    return 0

@app.on_message(filters.command(["start"]))
def echo(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id,f"__Hello {message.from_user.mention}, I am Ebooks Finder Bot, Just send me a name of the Book and I will get you results from pdfdrive.com to right here.__")


@app.on_message(filters.text)
def bookname(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    search = message.text
    books = getbooks.getpage(search)
    msg = app.send_photo(message.chat.id, books[0].link, f'**{books[0].title}**\n\n__Year: {books[0].year}\nSize: {books[0].size}\nPages: {books[0].pages}\nDownloads: {books[0].downloads}__', reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton( text='⬅️', callback_data="-1"),
                    InlineKeyboardButton( text='✅', callback_data="D0"),
                    InlineKeyboardButton( text='➡️', callback_data="+1")
                ]]))
    storedata(msg.id,books)


@app.on_callback_query()
def inbtwn(client: pyrogram.client.Client, call: pyrogram.types.CallbackQuery):

    # check for validity
    books = getdata(call.message.id)
    if books == 0:
        wrongimage = "https://w7.pngwing.com/pngs/389/161/png-transparent-sign-symbol-x-mark-check-mark-christian-cross-symbol-miscellaneous-angle-logo-thumbnail.png"
        app.edit_message_media(call.message.chat.id, call.message.id, InputMediaPhoto(wrongimage, "__Out of Date, Search Again__"))
        return
    
    # download
    if call.data[0] == "D":
        choose = int(call.data.replace("D",""))
        app.edit_message_text(call.message.chat.id, call.message.id, "__Downloading__")
        durl = getbooks.getdownlink(books[choose])
        res = requests.get(durl)
        with open(f"{books[choose].title}.pdf", "wb") as file:
            file.write(res.content)
        res = requests.get(books[choose].coverlink)
        with open(f"{books[choose].title}.jpg", "wb") as file:
            file.write(res.content)
        app.edit_message_text(call.message.chat.id, call.message.id, "__Uploading__")
        app.edit_message_media(call.message.chat.id, call.message.id, InputMediaDocument(f"{books[choose].title}.pdf", thumb=f"{books[choose].title}.jpg", caption=f"**{books[choose].title}**"))
        os.remove(f"{books[choose].title}.pdf")
        os.remove(f"{books[choose].title}.jpg")
        return

    #  next
    choose = int(call.data)
    app.edit_message_media(call.message.chat.id, call.message.id, InputMediaPhoto(books[choose].link, f'**{books[choose].title}**\n\n__Year: {books[choose].year}\nSize: {books[choose].size}\nPages: {books[choose].pages}\nDownloads: {books[choose].downloads}__') , reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton( text='⬅️', callback_data=str(choose-1)),
                    InlineKeyboardButton( text='✅', callback_data=f'D{choose}'),
                    InlineKeyboardButton( text='➡️', callback_data=str(choose+1))
                ]]))


    
# infinty polling
app.run()
