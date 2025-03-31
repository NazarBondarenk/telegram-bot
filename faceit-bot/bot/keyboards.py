from telegram import ReplyKeyboardMarkup

def get_menu_keyboard():
    keyboard = [
        ["Player info"],  
        ["Matches info"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)