import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging

import config
import os
from help import help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=config.token)
dispatcher = updater.dispatcher


def start(bot, update):
    print('Started')
    words = open('startWords.txt', 'r').read()
    print(words)
    bot.send_message(chat_id=update.message.chat.id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=words)


def find(bot, update):
    products = [i.replace(' ', '') for i in update.message.text.replace('/find', '').split(', ')]
    print(products)
    for file in os.listdir('recipes/'):
        filename = os.fsdecode(file)
        prods = getProducts(filename.split('.')[0])

        ok = True
        for i in prods:
            if i.strip() not in products:
                ok = False
        print(ok)
        if (ok):
            rec = open(os.path.join('recipes/', filename), 'r').read()
            print(rec)
            bot.send_message(chat_id=update.message.chat.id,
                             text=open(os.path.join('recipes/', filename), 'r').read())


def recipe(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text=open('recipes/' + update.message.text.split(' ')[-1] + '.recipe', 'r').read())


def getProducts(i):
    productsWithAmounts = open('recipes/{}.recipe'.format(i), 'r').read().split('--------')[1].split('\n')
    return sorted([i.split(':')[0] for i in productsWithAmounts])[2:]


def addRecipe(bot, update):
    recipe = [i.strip() for i in update.message.text.replace('/add', '').split('\n') if i != ' ']
    # print(recipe)
    num = str(update.message.chat.id) + ':' + str(len(os.listdir('recipes/')))
    name = recipe[recipe.index('Name:') + 1]
    products = [i.replace('-', ':') for i in recipe[recipe.index('Products:') + 1:recipe.index('Recipe:')]]
    recipe_itself = recipe[recipe.index('Recipe:') + 1:]

    '''print(num)
    print(name)
    print('-----')
    [print(i) for i in products]
    print('-----')
    [print(i) for i in recipe_itself]'''

    rec_file = open('recipes/' + num + '.recipe', 'w')
    rec_file.write(name + '\n')
    rec_file.write('--------\n')
    [rec_file.write(i + '\n') for i in products]
    rec_file.write('--------\n')
    [rec_file.write(i + '\n') for i in recipe_itself]
    rec_file.close()

    bot.send_message(chat_id=update.message.chat.id, text='Yor recipe was added, its number is {}'.format(num))
    return 0




def helpFunc(bot, update):
    try:
        command = update.message.text.split(' ')[-1].strip()
        #print(help)
        bot.send_message(chat_id=update.message.chat.id, text=help[command])
    except:
        bot.send_message(chat_id=update.message.chat.id, text="There is no such command")


#добавить хэлп хэндлер
if __name__ == '__main__':
    start_handler = CommandHandler('start', start)
    find_handler = CommandHandler('find', find)
    recipe_handler = CommandHandler('recipe', recipe)
    addRecipe_handler = CommandHandler('add', addRecipe)
    help_handler = CommandHandler('help',helpFunc)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(find_handler)
    dispatcher.add_handler(recipe_handler)
    dispatcher.add_handler(addRecipe_handler)
    dispatcher.add_handler(help_handler)

    updater.start_polling()
