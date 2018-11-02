import telegram
from telegram import KeyboardButton

standard_markup = telegram.ReplyKeyboardMarkup([[KeyboardButton(text='/start'), KeyboardButton(text='help')],
                                                [KeyboardButton(text='commands')]])

empty_markup = telegram.ReplyKeyboardRemove()

commands_markup = telegram.ReplyKeyboardMarkup([[KeyboardButton(text='find recipe'), KeyboardButton(text='add recipe'), KeyboardButton(text='my recipes')],
                                                [KeyboardButton(text='like'), KeyboardButton(text='dislike'), KeyboardButton('get likes')],
                                                [KeyboardButton(text='comment recipe'), KeyboardButton(text='get comments')],
                                                [KeyboardButton(text="recipe"), KeyboardButton(text="Back")]])

cancel_markup = telegram.ReplyKeyboardMarkup([[KeyboardButton(text='/cancel')]])
