from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton

def getButtons(choose=0):
    return InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton( text='⬅️', callback_data=str(choose-1)),
                            InlineKeyboardButton( text='✅', callback_data=f'D{choose}'),
                            InlineKeyboardButton( text='➡️', callback_data=str(choose+1))
                        ]])