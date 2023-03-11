import os
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton, InputMediaPhoto
from buttons import getButtons
import pdfdrive
import libgen
import annas
import hunter
import zlibrary
from openlibrary import openlibrary


bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)
wrongimage = "https://w7.pngwing.com/pngs/389/161/png-transparent-sign-symbol-x-mark-check-mark-christian-cross-symbol-miscellaneous-angle-logo-thumbnail.png"

# zlibrary
remix_id = os.environ.get("REMIX_ID", None)
remix_key = os.environ.get("REMIX_KEY", None)
zemail = os.environ.get("Z_EMAIL", None)
zpass = os.environ.get("Z_PASS", None)
if remix_id is not None and remix_key is not None: Z = zlibrary.Zlibrary(remix_userid=remix_id, remix_userkey=remix_key)
elif zemail is not None and zpass is not None: Z = zlibrary.Zlibrary(email=zemail, password=zpass)
else: Z = None
if Z and not Z.isLogin(): raise("Wrong Credentials")


data = {}
site = {}
Null = "Null"
def storedata(msgid,books,website):
    data[msgid] = books
    site[msgid] = website

def getdata(msgid):
    return data.get(msgid,None), site.get(msgid,None)

def removedata(msgid):
    data[msgid] = Null
    site[msgid] = Null


sites =  [
            "pdfdrive",
            "librarygenesis",
            "annas",
            "hunter",
            "zlib",
         ]
def isSite(calldata):
    for ele in sites:
        if ele in calldata: return True
    return False


@app.on_message(filters.command(["start","help"]))
def echo(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id,
        f"__Hello {message.from_user.mention}, \
I am Ebooks Finder Bot, Just send me a name of the Book and I will get you results from \
[PdfDrive](https://pdfdrive.com), \
[Library Genesis](https://libgen.li/), \
[eBook-Hunter](https://ebook-hunter.org/), \
[Anna's Archive](https://annas-archive.org/), \
and [Zlibrary](http://z-lib.org/) to right here.__", reply_to_message_id=message.id, disable_web_page_preview=True)


def handleASCM(file, message):
    msg = app.send_message(message.chat.id, "__Processing__", reply_to_message_id=message.id)
    try: ofile = openlibrary.main(file,None)
    except: ofile is None
    os.remove(file)

    if ofile is not None:
        app.edit_message_text(message.chat.id, msg.id, "__Uploading__")
        app.send_document(message.chat.id, ofile, reply_to_message_id=message.id)
        app.delete_messages(message.chat.id, msg.id)
        os.remove(ofile)
    else:
        app.edit_message_text(message.chat.id, msg.id, "__Failed, problem in Decrypting__")


@app.on_message(filters.document)
def acsmfile(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    file = app.download_media(message)
    handleASCM(file, message)


@app.on_message(filters.text)
def bookname(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, '__choose website to get result from__', reply_to_message_id=message.id, reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton( text='Library Genesis', callback_data=f"librarygenesis {message.chat.id} {message.id}")],
                    [InlineKeyboardButton( text='PDF Drive', callback_data=f"pdfdrive {message.chat.id} {message.id}")],
                    [InlineKeyboardButton( text='eBook Hunter', callback_data=f"hunter {message.chat.id} {message.id}")],
                    [InlineKeyboardButton( text='Annas Archive', callback_data=f"annas {message.chat.id} {message.id}")],
                    [InlineKeyboardButton( text='Zlibrary', callback_data=f"zlib {message.chat.id} {message.id}")],
                ]))
    

@app.on_callback_query()
def handle(client: pyrogram.client.Client, call: pyrogram.types.CallbackQuery):

    # site selection
    if isSite(call.data):
        app.answer_callback_query(call.id,"processing...")
        data = call.data.split()
        message:pyrogram.types.messages_and_media.message.Message = app.get_messages(data[1], int(data[2]))
        search = message.text

        # pdfdrive
        if data[0] == "pdfdrive":
            books = pdfdrive.getpage(search)
            if len(books) == 0:
                app.send_message(message.chat.id,f"__PDFdrive : No results found__", reply_to_message_id=message.id)
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
                app.send_message(message.chat.id,f"__LibraryGenesis : No results found__", reply_to_message_id=message.id)
            else:
                msg = app.send_photo(message.chat.id, libgen.getBookImg(books[0]),
                    libgen.getLibText(books), reply_to_message_id=message.id, reply_markup=getButtons())
                storedata(msg.id,books,"librarygenesis")
        

        # annas archive
        elif data[0] == "annas":
            books = annas.getAnnasBooks(search)
            if books is None:
                app.send_message(message.chat.id,f"__Not able to Connect, maybe Cloudflare protection__", reply_to_message_id=message.id)
            elif len(books) == 0:
                app.send_message(message.chat.id,f"__Annas archive : No results found__", reply_to_message_id=message.id)
            else:
                msg = app.send_photo(message.chat.id, books[0]["cover"],
                    annas.getAnnasText(books), reply_to_message_id=message.id, reply_markup=getButtons())
                storedata(msg.id,books,"annas")
        
        # ebook hunter
        elif data[0] == "hunter":
            books = hunter.getHunterBooks(search)
            if len(books) == 0:
                app.send_message(message.chat.id,f"__Ebook Hunter : No results found__", reply_to_message_id=message.id)
            else:
                msg = app.send_photo(message.chat.id, books[0]["cover"],
                    hunter.getHuntText(books), reply_to_message_id=message.id, reply_markup=getButtons())
                storedata(msg.id,books,"hunter")

        # zlib
        elif data[0] == "zlib":
            if not Z:
               app.send_message(message.chat.id,f"__Required variables are not set, you can't use Zlibrary__", reply_to_message_id=message.id) 
               return
            
            check, books = zlibrary.getZlibBooks(Z,search)
            if not check:
                app.send_message(message.chat.id,f"__{books}__", reply_to_message_id=message.id)
            elif len(books) == 0:
                app.send_message(message.chat.id,f"__Zlibrary : No results found__", reply_to_message_id=message.id)
            else:
                msg = app.send_photo(message.chat.id, zlibrary.getImage(Z, books[0]),
                    zlibrary.getZlibText(books), reply_to_message_id=message.id, reply_markup=getButtons())
                storedata(msg.id,books,"zlib")    
        
        # end
        return

    # check for validity
    books, website = getdata(call.message.id)
    if books == Null and website == Null: return
    if books == None:
        app.edit_message_media(call.message.chat.id, call.message.id, InputMediaPhoto(wrongimage, "__Out of Date, Search Again__"))
        return

    if call.data[0] == "D": removedata(call.message.id)
    downloded = False

    # pdfdrive
    if website == "pdfdrive":
        downloded = pdfdrive.handlePdfdrive(app,call,books)

    # librarygenesis
    elif website == "librarygenesis":
        downloded = libgen.handleLibGen(app,call,books)
    
    # annas
    elif website == "annas":
        downloded = annas.handleAnnas(app,call,books)
    
    # hunter
    elif website == "hunter":
        downloded = hunter.handleHunt(app,call,books)

    # zlibraray
    elif website == "zlib":
        downloded = zlibrary.handleZlib(Z,app,call,books)

    # if downloded: 
    #     removedata(call.message.id)

# infinty polling
app.run()
