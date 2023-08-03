from os import remove
from requests import get
# from bs4 import BeautifulSoup
from pyrogram.types import InputMediaPhoto, CallbackQuery #InputMediaDocument
from pyrogram import Client
from buttons import getButtons

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
        book["coverlink"] = ele.get("thumbline",wrongimage)
        book["title"] = ele["name"]
        book["author"] = ele["author"]
        book["pages"] = str(ele["page"])
        book["year"] = str(ele["release_year"])
        book["size"] = str(ele["file_size"]) + "MB"
        book["downloads"] = book["link"]
        book["lang"] = ele["language"]
        books.append(book)

    return books


# def getdownlink(book):

#     headers = {
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#     'Accept-Language': 'en-US,en;q=0.5',
#     'Referer': book.link,
#     'Alt-Used': 'www.pdfdrive.to',
#     'Connection': 'keep-alive',
#     'Upgrade-Insecure-Requests': '1',
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'same-origin',
#     'Sec-Fetch-User': '?1',

#     }

#     url = book.link.replace(f'e{book.id}',f"d{book.id}")
#     response = get(url, headers=headers)
#     soup = BeautifulSoup(response.text,"html.parser").findAll("script")[6].get_text()
    
#     temp = soup.split("{")
#     for ele in temp:
#         if "id" in ele and "session" in ele:
#             id = ele.split("'")[1]
#             sess = ele.split("'")[3]

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
#         'Accept': '*/*',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'X-Requested-With': 'XMLHttpRequest',
#         'Alt-Used': 'www.pdfdrive.to',
#         'Connection': 'keep-alive',
#         'Referer': url,
#         'Sec-Fetch-Dest': 'empty',
#         'Sec-Fetch-Mode': 'cors',
#         'Sec-Fetch-Site': 'same-origin',
#             }

#     params = { 'id': id, 'session': sess,}

#     response = get('https://www.pdfdrive.to/ebook/broken', params=params,  headers=headers)
#     soup = BeautifulSoup(response.text,"html.parser")
#     res = soup.find("a").get('href')

#     if "http" in res:
#         durl = res
#     else:
#         durl = f'https://www.pdfdrive.to/download.pdf?id={id}&h={sess}&u=cache&ext=pdf' # or "https://www.pdfdrive.to" + res
    
#     print(durl)
#     return durl


def getPdfText(books,choose=0):
    return f'**{books[choose]["title"]}**\n\n__Year: {books[choose]["year"]}\nSize: {books[choose]["size"]}\nPages: {books[choose]["pages"]}\nAuthor: {books[choose]["author"]}\Language: {books[choose]["lang"]}__' \
    + "\n\n------[PDFdrive]------" + f"  [{choose+1}/{len(books)}]"


def handlePdfdrive(app:Client,call:CallbackQuery,books:list):

    # download
        if call.data[0] == "D":
            choose = int(call.data.replace("D",""))
            app.edit_message_text(call.message.chat.id, call.message.id, f'**{books[choose]["title"]}**\n\n__External Link : {books[choose]["downloads"]}__')
            return True
        
            # app.edit_message_text(call.message.chat.id, call.message.id, "__Downloading__")
            # durl = getdownlink(books[choose])
            # res = get(durl)
            # filename = f"{books[choose].title}"
            # filename = "".join( x for x in filename if (x.isalnum() or x in "_ ")) + ".pdf"
            # with open(filename, "wb") as file:
            #     file.write(res.content)
            # res = get(books[choose].coverlink)
            # thumbfile = f"{books[choose].title}"
            # thumbfile = "".join( x for x in thumbfile if (x.isalnum() or x in "_ ")) + ".jpg"
            # with open(thumbfile, "wb") as file:
            #     file.write(res.content)
            # app.edit_message_text(call.message.chat.id, call.message.id, "__Uploading__")
            # app.edit_message_media(call.message.chat.id, call.message.id, InputMediaDocument(filename, thumb=thumbfile, caption=f"**{books[choose].title}**"))
            # remove(filename)
            # remove(thumbfile)
            
        #  next
        choose = int(call.data) % len(books)
        try:
            app.edit_message_media(call.message.chat.id, call.message.id,
            InputMediaPhoto(books[choose]["coverlink"],getPdfText(books,choose)),
            reply_markup=getButtons(choose))
        except:
            app.edit_message_media(call.message.chat.id, call.message.id,
            InputMediaPhoto(books[choose]["link"],getPdfText(books,choose)),
            reply_markup=getButtons(choose))
        return False
