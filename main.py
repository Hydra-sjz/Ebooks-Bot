import os
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton, InputMediaPhoto
from buttons import getButtons
import pdfdrive
import libgen
import annas


bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)
wrongimage = "https://w7.pngwing.com/pngs/389/161/png-transparent-sign-symbol-x-mark-check-mark-christian-cross-symbol-miscellaneous-angle-logo-thumbnail.png"


data = {}
site = {}
def storedata(msgid,books,website):
    data[msgid] = books
    site[msgid] = website

def getdata(msgid):
    return data.get(msgid,None), site.get(msgid,None)
                        

@app.on_message(filters.command(["start"]))
def echo(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id,
        f"__Hello {message.from_user.mention}, I am Ebooks Finder Bot, Just send me a name of the Book and I will get you results from [PdfDrive](https://pdfdrive.com) and [Library Genesis](https://libgen.li/) to right here.__",
        reply_to_message_id=message.id, disable_web_page_preview=True)


@app.on_message(filters.text)
def bookname(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, '__choose website to get result from__', reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton( text='PDF Drive', callback_data=f"pdfdrive {message.chat.id} {message.id}")],
                    [InlineKeyboardButton( text='Library Genesis', callback_data=f"librarygenesis {message.chat.id} {message.id}")],
                    [InlineKeyboardButton( text='Annas Archive', callback_data=f"annas {message.chat.id} {message.id}")]
                ]))
    

@app.on_callback_query()
def handle(client: pyrogram.client.Client, call: pyrogram.types.CallbackQuery):

    # site selection
    if "pdfdrive" in call.data or "librarygenesis" in call.data or "annas" in call.data:
        app.answer_callback_query(call.id,"processing...")
        data = call.data.split()
        message:pyrogram.types.messages_and_media.message.Message = app.get_messages(data[1], int(data[2]))
        search = message.text

        # pdfdrive
        if data[0] == "pdfdrive":
            books = pdfdrive.getpage(search)
            if len(books) == 0:
                app.send_message(message.chat.id,f"__No results found__", reply_to_message_id=message.id)
            else:
                try:
                    msg = app.send_photo(message.chat.id, books[0].link,
                    pdfdrive.getPdfText(books),
                    reply_to_message_id=message.id, reply_markup=getButtons())
                except:
                    msg = app.send_photo(message.chat.id, books[0].coverlink,
                    pdfdrive.getPdfText(books),
                    reply_to_message_id=message.id, reply_markup=getButtons())
                storedata(msg.id,books,"pdfdrive")
        
        # librarygenesis
        elif data[0] == "librarygenesis":
            books = libgen.getBooks(search)
            if len(books) == 0:
                app.send_message(message.chat.id,f"__No results found__", reply_to_message_id=message.id)
            else:
                msg = app.send_photo(message.chat.id, libgen.getBookImg(books[0]),
                    libgen.getLibText(books), reply_to_message_id=message.id, reply_markup=getButtons())
                storedata(msg.id,books,"librarygenesis")
        

        # annas archive
        elif data[0] == "annas":
            books = annas.getAnnasBooks(search)
            if len(books) == 0:
                app.send_message(message.chat.id,f"__No results found__", reply_to_message_id=message.id)
            else:
                msg = app.send_photo(message.chat.id, books[0]["cover"],
                    annas.getAnnasText(books), reply_to_message_id=message.id, reply_markup=getButtons())
                storedata(msg.id,books,"annas")
        
        # end
        return

    # check for validity
    books, website = getdata(call.message.id)
    if books == None:
        app.edit_message_media(call.message.chat.id, call.message.id, InputMediaPhoto(wrongimage, "__Out of Date, Search Again__"))
        return

    # pdfdrive
    if website == "pdfdrive":
        pdfdrive.handlePdfdrive(app,call,books)

    # librarygenesis
    elif website == "librarygenesis":
        libgen.handleLibGen(app,call,books)
    
    # annas
    elif website == "annas":
        annas.handleAnnas(app,call,books)
            
            
# infinty polling
app.run()
