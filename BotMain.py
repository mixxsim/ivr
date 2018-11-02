import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, RegexHandler
from telegram.ext.filters import Filters
import logging

import config
import markups
import os
from help import help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

updater = Updater(token=config.token)
dispatcher = updater.dispatcher


def start(bot, update):
    print('Started')
    words = open('startWords.txt', 'r', encoding='utf-8').read()
    print(words)
    bot.send_message(chat_id=update.message.chat.id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=words,
                     reply_markup=markups.standard_markup)


def showCommands(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="Command Menu",
                     reply_markup=markups.commands_markup)


def show_main_menu(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="Main Menu",
                     reply_markup=markups.standard_markup)


# find recipe block START
def getRecipeProducts(i):
    print(i)
    productsWithAmounts = open('recipes/{}.recipe'.format(i), 'r', encoding='utf-8').read().split('--------')[1].split(
        '\n')
    return sorted([i.split(':')[0] for i in productsWithAmounts])[2:]


def find_intro(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="Print products to find a receipt with",
                     reply_markup=markups.cancel_markup)
    return 0


def find(bot, update):
    products = [i.lower().strip() for i in update.message.text.split(',')]
    print(products)
    for file in os.listdir('recipes/'):
        prods = getRecipeProducts(file.split('.')[0])
        if (prods == []):
            break

        ok = True
        print(prods)
        for i in prods:
            if i.strip() not in products and i != '':
                ok = False
        print(ok)
        if (ok):
            rec = open(os.path.join('recipes/', file), 'r', encoding='utf-8').read()
            print(rec)
            bot.send_message(chat_id=update.message.chat.id,
                             text=rec.replace('мть', 'мл').replace('ть','л'),
                             reply_markup=markups.cancel_markup)

    bot.send_message(chat_id=update.message.chat.id,
                     text="That's all",
                     reply_markup=markups.commands_markup)
    return ConversationHandler.END


# find recipe block END


# get recipe by ID block START
def recipe_intro(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="What is the ID of recipe you want to watch?",
                     reply_markup=markups.cancel_markup)
    return 0


def recipe(bot, update):
    ID = update.message.text
    bot.send_message(chat_id=update.message.chat.id,
                     text='id: {}\n'.format(ID) + open('recipes/' + ID + '.recipe', 'r').read().replace('мть', 'мл').replace('ть','л'),
                     reply_markup=markups.commands_markup)
    return ConversationHandler.END


# get recipe by ID block END

# add recipe block START
tmp_name = ''
tmp_prod = ''
tmp_recipe = ''


def add_recipe_intro(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="First, type a name of your recipe",
                     reply_markup=markups.cancel_markup)
    return 0


def getName(bot, update):
    global tmp_name
    tmp_name = update.message.text.strip()
    bot.send_message(chat_id=update.message.chat.id,
                     text="Ok, now give the products in special format (check out help)",
                     reply_markup=markups.cancel_markup)
    return 1


def getProducts(bot, update):
    global tmp_prod
    tmp_prod = update.message.text.upper()
    bot.send_message(chat_id=update.message.chat.id,
                     text="Ok, now give the steps of the recipe",
                     reply_markup=markups.cancel_markup)
    return 2


def getSteps(bot, update):
    global tmp_prod, tmp_name
    tmp_recipe = update.message.text

    num = str(update.message.chat.id) + '_' + str(len(os.listdir('recipes/')))
    rec_file = open('recipes/' + num + '.recipe', 'w')
    rec_file.write(tmp_name + '\n')
    rec_file.write('--------\n')
    rec_file.write(tmp_prod + '\n')
    rec_file.write('--------\n')
    rec_file.write(tmp_recipe)
    rec_file.close()

    bot.send_message(chat_id=update.message.chat.id,
                     text="Ok, your recipe is writtent down. ID:{}".format(num),
                     reply_markup=markups.commands_markup)
    return ConversationHandler.END


# add recipe block END

# get my recipes block START
def get_my_recipes(bot, update):
    my = []
    for file in os.listdir('recipes/'):
        if (str(update.message.chat.id) + '_' in file):
            my.append(file)
    repl = '\n'.join([i + ' : ' + open('recipes/{}'.format(i), 'r').readline().strip() for i in my])
    if repl == '':
        repl = 'You have no added recipes yet'
    bot.send_message(chat_id=update.message.chat.id,
                     text=repl,
                     reply_markup=markups.commands_markup)


# get my recipes block END

# add comment block BEGIN
tmp_id = ''


def add_comment_intro(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="What is the ID of the recipe to add comment to?",
                     reply_markup=markups.cancel_markup)
    return 0


def get_id_for_comment(bot, update):
    global tmp_id
    tmp_id = update.message.text
    bot.send_message(chat_id=update.message.chat.id,
                     text="Ok, now type in the comment itself",
                     reply_markup=markups.cancel_markup)
    return 1


def addComment(bot, update):
    global tmp_id
    recipe, comment = tmp_id, update.message.text.strip()
    com = open('comments/' + recipe + '_' + str(update.message.chat.id) + '.comment', 'a')
    com.write(comment.strip() + '\n')
    com.close()
    print('User {} added comment to recipe {}'.format(update.message.chat.id, recipe))
    bot.send_message(chat_id=update.message.chat.id,
                     text="Nice! Your comment is written down!",
                     reply_markup=markups.commands_markup)

    return ConversationHandler.END


# add comment block END

# get comment block START
def see_comment_intro(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="What the ID of the recipe to get comments to?",
                     reply_markup=markups.cancel_markup)
    return 0


def seeComment(bot, update):
    recipe = update.message.text.strip()
    try:
        com = open('comments/' + recipe + '_' + str(update.message.chat.id) + '.comment', 'r').read()
        bot.send_message(chat_id=update.message.chat.id,
                         text=com,
                         reply_markup=markups.commands_markup)
        print('User {} got his comments to recipe {}'.format(update.message.chat.id, recipe))
    except:
        bot.send_message(chat_id=update.message.chat.id,
                         text="Yet you have no comments to this recipe",
                         reply_markup=markups.commands_markup)

    return ConversationHandler.END


# get comment block END

# like block START
def like_intro(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="What is ID of the recipe you like?",
                     reply_markup=markups.cancel_markup)
    return 0


def like(bot, update):
    recipe = update.message.text.strip()
    try:
        open('recipes/{}.recipe'.format(recipe), 'r').read()
    except:
        bot.send_message(chat_id=update.message.chat.id,
                         text="There is no recipe with such ID",
                         reply_markup=markups.commands_markup)
        return ConversationHandler.END
    likesList = open('likes/' + str(update.message.chat.id) + '.likes', 'a')
    likesList.write(update.message.text.split('\n')[-1] + '\n')
    likesList.close()
    print('User {} liked recipe {}'.format(update.message.chat.id, recipe))
    bot.send_message(chat_id=update.message.chat.id,
                     text="Mmmm, nice choice!",
                     reply_markup=markups.commands_markup)
    return ConversationHandler.END


# like block END

# dislike block START
def dislike_intro(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="What recipe you dislike?",
                     reply_markup=markups.cancel_markup)
    return 0


def dislike(bot, update):
    try:
        recipe = update.message.text.strip()
        open('recipes/{}.recipe'.format(recipe), 'r')
        likesList = open('likes/' + str(update.message.chat.id) + '.likes', 'r').read()
        likesList = likesList.replace('{}\n'.format(recipe), '')
        open('likes/' + str(update.message.chat.id) + '.likes', 'w').write(likesList)
        print('User {} disliked recipe {}'.format(update.message.chat.id, recipe))
    except FileNotFoundError:
        bot.send_message(chat_id=update.message.chat.id,
                         text="No recipe with such ID",
                         reply_markup=markups.commands_markup)
    except:
        bot.send_message(chat_id=update.message.chat.id,
                         text="You haven't liked anything yet",
                         reply_markup=markups.commands_markup)
    bot.send_message(chat_id=update.message.chat.id,
                     text="Ok, may be you'll relike it later",
                     reply_markup=markups.commands_markup)
    return ConversationHandler.END


# dislike block END

# get likes block START
def getLikes(bot, update):
    try:
        likes = list(
            sorted(set(open('likes/' + str(update.message.chat.id) + '.likes', 'r').read().strip().split('\n'))))
        print(likes)
        repl = '\n'.join([i + ' : ' + open('recipes/{}.recipe'.format(i), 'r').readline().strip() for i in likes])
        bot.send_message(chat_id=update.message.chat.id,
                         text=repl,
                         reply_markup=markups.commands_markup)
        print('User {} got his likes'.format(update.message.chat.id))
    except Exception as e:
        print(e.args)
        bot.send_message(chat_id=update.message.chat.id,
                         text="You haven't liked anything yet",
                         reply_markup=markups.commands_markup)
    return 0


# get likes block END

# help block START
def help_intro(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                     text="Which command do you want to get help for?",
                     reply_markup=markups.cancel_markup)
    return 0


def helpFunc(bot, update):
    command = update.message.text.strip()
    if command in help:
        # print(help)
        bot.send_message(chat_id=update.message.chat.id,
                         text=help[command],
                         reply_markup=markups.standard_markup)
    else:
        bot.send_message(chat_id=update.message.chat.id,
                         text="There is no such command",
                         reply_markup=markups.standard_markup)

    return ConversationHandler.END


# help block END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Cancelled', reply_markup=markups.commands_markup)

    return ConversationHandler.END


# ToDo add buttons
if __name__ == '__main__':
    start_handler = CommandHandler('start', start)
    showCommand_handler = RegexHandler('^commands$', showCommands)
    show_main_menu_handler = RegexHandler('^Back$', show_main_menu)
    get_my_recipes_handler = RegexHandler('^my recipes$', get_my_recipes)
    getLikes_handler = RegexHandler('^get likes$', getLikes)

    help_conv_handler = ConversationHandler(
        entry_points=[RegexHandler('^help$', help_intro)],
        states={
            0: [MessageHandler(Filters.text, helpFunc)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    find_conv_handler = ConversationHandler(
        entry_points=[RegexHandler('^find recipe$', find_intro)],
        states={
            0: [MessageHandler(Filters.text, find)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    add_recipe_conv_handler = ConversationHandler(
        entry_points=[RegexHandler('^add recipe$', add_recipe_intro)],
        states={
            0: [MessageHandler(Filters.text, getName)],
            1: [MessageHandler(Filters.text, getProducts)],
            2: [MessageHandler(Filters.text, getSteps)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    get_recipe_conv_handler = ConversationHandler(
        entry_points=[RegexHandler('^recipe$', recipe_intro)],
        states={
            0: [MessageHandler(Filters.text, recipe)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    add_comment_conv_handler = ConversationHandler(
        entry_points=[RegexHandler('^comment recipe$', add_comment_intro)],
        states={
            0: [MessageHandler(Filters.text, get_id_for_comment)],
            1: [MessageHandler(Filters.text, addComment)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    get_comment_conv_handler = ConversationHandler(
        entry_points=[RegexHandler("^get comments$", see_comment_intro)],
        states={
            0: [MessageHandler(Filters.text, seeComment)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    like_conv_handler = ConversationHandler(
        entry_points=[RegexHandler("^like$", like_intro)],
        states={
            0: [MessageHandler(Filters.text, like)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dislike_conv_handler = ConversationHandler(
        entry_points=[RegexHandler("^dislike$", dislike_intro)],
        states={
            0: [MessageHandler(Filters.text, dislike)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(showCommand_handler)
    dispatcher.add_handler(show_main_menu_handler)
    dispatcher.add_handler(help_conv_handler)
    dispatcher.add_handler(find_conv_handler)
    dispatcher.add_handler(get_recipe_conv_handler)
    dispatcher.add_handler(add_recipe_conv_handler)
    dispatcher.add_handler(get_my_recipes_handler)
    dispatcher.add_handler(add_comment_conv_handler)
    dispatcher.add_handler(get_comment_conv_handler)
    dispatcher.add_handler(like_conv_handler)
    dispatcher.add_handler(dislike_conv_handler)
    dispatcher.add_handler(getLikes_handler)

    updater.start_polling()
