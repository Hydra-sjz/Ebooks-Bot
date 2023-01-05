import os
import pyrogram
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton, InputMediaPhoto, InputMediaDocument
import getbooks
import requests
import libgen


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

def getButtons(choose=0):
    return InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton( text='⬅️', callback_data=str(choose-1)),
                            InlineKeyboardButton( text='✅', callback_data=f'D{choose}'),
                            InlineKeyboardButton( text='➡️', callback_data=str(choose+1))
                        ]])
                        

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
                    [InlineKeyboardButton( text='Library Genesis', callback_data=f"librarygenesis {message.chat.id} {message.id}")]
                ]))
    

@app.on_callback_query()
def inbtwn(client: pyrogram.client.Client, call: pyrogram.types.CallbackQuery):

    # site selection
    if "pdfdrive" in call.data or "librarygenesis" in call.data:
        app.answer_callback_query(call.id,"processing...")
        data = call.data.split()
        message = app.get_messages(data[1], int(data[2]))
        search = message.text

        # pdfdrive
        if data[0] == "pdfdrive":
            books = getbooks.getpage(search)
            if len(books) == 0:
                app.send_message(message.chat.id,f"__No results found__", reply_to_message_id=message.id)
            else:
                msg = app.send_photo(message.chat.id, books[0].link,
                    f'**{books[0].title}**\n\n__Year: {books[0].year}\nSize: {books[0].size}\nPages: {books[0].pages}\nDownloads: {books[0].downloads}__',
                    reply_to_message_id=message.id, reply_markup=getButtons())
                storedata(msg.id,books,"pdfdrive")
        
        # librarygenesis
        elif data[0] == "librarygenesis":
            books = libgen.getBooks(search)
            if len(books) == 0:
                app.send_message(message.chat.id,f"__No results found__", reply_to_message_id=message.id)
            else:
                msg = app.send_photo(message.chat.id, libgen.getBookImg(books[0]),
                    f'**{books[0]["Title"]}**\n\n__Author: {books[0]["Author"]}\nPublisher: {books[0]["Publisher"]}\nYear: {books[0]["Year"]}\nSize: {books[0]["Size"]}\nPages: {books[0]["Pages"]}\nLanguage: {books[0]["Language"]}\nExtension: {books[0]["Extension"]}__',
                    reply_to_message_id=message.id, reply_markup=getButtons())
                storedata(msg.id,books,"librarygenesis")
        
        # end
        return


    # check for validity
    books, website = getdata(call.message.id)
    if books == None:
        app.edit_message_media(call.message.chat.id, call.message.id, InputMediaPhoto(wrongimage, "__Out of Date, Search Again__"))
        return
    

    # pdfdrive
    if website == "pdfdrive":
        
        # download
        if call.data[0] == "D":
            choose = int(call.data.replace("D",""))
            app.edit_message_text(call.message.chat.id, call.message.id, "__Downloading__")
            durl = getbooks.getdownlink(books[choose])
            res = requests.get(durl)
            filename = f"{books[choose].title}"
            filename = "".join( x for x in filename if (x.isalnum() or x in "_ ")) + ".pdf"
            with open(filename, "wb") as file:
                file.write(res.content)
            res = requests.get(books[choose].coverlink)
            thumbfile = f"{books[choose].title}"
            thumbfile = "".join( x for x in thumbfile if (x.isalnum() or x in "_ ")) + ".jpg"
            with open(thumbfile, "wb") as file:
                file.write(res.content)
            app.edit_message_text(call.message.chat.id, call.message.id, "__Uploading__")
            app.edit_message_media(call.message.chat.id, call.message.id, InputMediaDocument(filename, thumb=thumbfile, caption=f"**{books[choose].title}**"))
            os.remove(filename)
            os.remove(thumbfile)
            return

        #  next
        choose = int(call.data) % len(books)
        app.edit_message_media(call.message.chat.id, call.message.id,
            InputMediaPhoto(books[choose].link,
            f'**{books[choose].title}**\n\n__Year: {books[choose].year}\nSize: {books[choose].size}\nPages: {books[choose].pages}\nDownloads: {books[choose].downloads}__'),
            reply_markup=getButtons(choose))


    # librarygenesis
    if website == "librarygenesis":

        # download
        if call.data[0] == "D":
            choose = int(call.data.replace("D",""))
            app.edit_message_text(call.message.chat.id, call.message.id, "__Downloading__")
            links = libgen.getDownLink(books[choose])
            i = 0
            while i<len(links):
                print(links[i])
                res = requests.get(links[i])
                if res.status_code == 200: break
            filename = f"{books[choose]['Title']}"
            filename = "".join( x for x in filename if (x.isalnum() or x in "_ ")) + f".{books[choose]['Extension']}"
            with open(filename, "wb") as file:
                file.write(res.content)

            res = requests.get(libgen.getBookImg(books[choose]))
            thumbfile = f"{books[choose]['Title']}"
            thumbfile = "".join( x for x in thumbfile if (x.isalnum() or x in "_ ")) + ".jpg"
            with open(thumbfile, "wb") as file:
                file.write(res.content)
            app.edit_message_text(call.message.chat.id, call.message.id, "__Uploading__")
            app.edit_message_media(call.message.chat.id, call.message.id, InputMediaDocument(filename, thumb=thumbfile, caption=f"**{books[choose]['Title']}**"))
            os.remove(filename)
            os.remove(thumbfile)
            return

        #  next
        choose = int(call.data) % len(books)
        app.edit_message_media(call.message.chat.id, call.message.id,
            InputMediaPhoto(libgen.getBookImg(books[choose]),
            f'**{books[choose]["Title"]}**\n\n__Author: {books[choose]["Author"]}\nPublisher: {books[choose]["Publisher"]}\nYear: {books[choose]["Year"]}\nSize: {books[choose]["Size"]}\nPages: {books[choose]["Pages"]}\nLanguage: {books[choose]["Language"]}\nExtension: {books[choose]["Extension"]}__'),
            reply_markup=getButtons(choose))
            
            
    
# infinty polling
app.run()
