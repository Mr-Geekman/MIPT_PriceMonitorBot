"""
Bot to monitor prices on Aliexpress.
"""

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from product_parser import ProductParser
from data_base_processor import DataBaseProcessor
import argparse
from check_args import *


class MonitorBotLogic:
    """
    Class with monitor logic
    """
    def __init__(self, data_base_path):
        self.data_base_path = data_base_path

    def refresh(self, bot, job):
        """
        Refresh all prices for all users
        """
        data_base = DataBaseProcessor(self.data_base_path)
        data = data_base.show_all()
        for entry in data:
            parser = ProductParser(entry[2])
            current_price = parser.prices[tuple(sorted(entry[3].split(',')))]
            if current_price != str(entry[4]):
                data_base.update(entry[0], entry[1], current_price)
                bot.send_message(entry[0],
                                 text="The price of the product {} has "
                                      "changed from {} "
                                      "to {}".format(entry[1], entry[4],
                                                     current_price))
        data_base.close()

    def start(self, bot, update):
        """
        Start the bot
        """
        update.message.reply_text("Hello! I am a bot, which can monitor "
                                  "prices on Aliexpress. Use /help to know, "
                                  "how to give commands to me.")

    def help(self, bot, update):
        """
        Show commands to user and its meanings
        """
        update.message.reply_text(
            "1) /add <link> <title> add a new product to monitor with its "
            "title (unique), after adding user have to choose the color "
            "of product\n"
            "2) /delete <title> delete a product from monitor list by title\n"
            "3) /show show prices for all added products"
        )

    def add(self, bot, update, args, chat_data):
        """
        Add a new product to monitor
        :param args: args[0] - link to product, args[1:] - title for product
        """
        try:
            link = args[0]
            title = ' '.join(args[1:])
            # Create a parser
            parser = ProductParser(link)
            if parser.prices:
                # Send user a buttons to choose color, size, type and etc
                property_is_empty = True
                for property, values in parser.properties.items():
                    property_is_empty = False
                    keyboard = [[InlineKeyboardButton(value,
                                                      callback_data=key)]
                                for key, value in values.items()]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text(
                        "Select {}".format(property.lower()),
                        reply_markup=reply_markup)
                # If product added correctly, but it hasn't any property
                if property_is_empty:
                    self.save(bot, update.message.chat_id, parser, title)
                else:
                    # Initialize chat_data if product has properties
                    chat_data['title'] = title
                    chat_data['parser'] = parser
                    chat_data['prop_ids'] = []
            else:
                update.message.reply_text("The link isn't correct")
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /add <link> <title> '
                                      'title should be unique')

    def show(self, bot, update):
        """
        Show all prices for all products
        """
        data_base = DataBaseProcessor(self.data_base_path)
        entries = data_base.show(update.message.chat_id)
        if entries:
            message_text = '\n'.join([': '.join(map(str, y[::3]))
                                      for y in entries])
        else:
            message_text = "At the moment you do not have any added products"
        update.message.reply_text(message_text)
        data_base.close()

    def delete(self, bot, update, args):
        """
        Delete the product with defined title
        :param args: args[0] - title of product
        """
        try:
            title = args[0]
            # Find entry in data base and delete it
            data_base = DataBaseProcessor(self.data_base_path)
            data_base.delete(update.message.chat_id, title)
            data_base.close()
        except(IndexError, ValueError):
            update.message.reply_text('Usage: /delete <title>')

    def choice(self, bot, update, chat_data):
        """
        Handle buttons' callbacks
        """
        query = update.callback_query
        # Fix user's choice
        bot.edit_message_text(text="Selected", chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        # Add info chat_data
        chat_data['prop_ids'].append(query.data)
        # If user made a full choice remember the price
        if len(chat_data['prop_ids']) == len(
                list(chat_data['parser'].prices)[0]):
            self.save(bot, query.message.chat_id, chat_data['parser'],
                      chat_data['title'], chat_data['prop_ids'])
            # Clean user's chat_data
            chat_data.clear()

    def save(self, bot, chat_id, parser, title, prop_ids=['']):
        """
        Save full selected product to data_base
        :param chat_id: id of chat with user
        :param parser: parser with info about product
        :param title: title of the product
        :param prop_ids: ids of product's properties
        """
        price = float(parser.prices[tuple(sorted(prop_ids))])
        data_base = DataBaseProcessor(self.data_base_path)
        if data_base.add(chat_id,
                         title,
                         parser.link,
                         ';'.join(prop_ids),
                         price):
            bot.send_message(text="Product {} has been added. At the moment "
                                  "it's price is {}".format(title, price),
                             chat_id=chat_id)
        else:
            bot.send_message(text="Product {} has already been added.".
                             format(title), chat_id=chat_id)
        # Close data_base
        data_base.close()


def parse_command_line_arguments():
    """
    Create a parser for parsing command line arguments and parse it
    :return: command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Bot to monitor prices on Aliexpress')
    parser.add_argument('--token', required=True, help='Token to run bot')
    parser.add_argument('--database', required=True,
                        type=lambda x: is_valid_file(parser, x),
                        help='Database path')
    parser.add_argument('--periodicity',
                        type=lambda x: is_positive_int(parser, x),
                        default=21600,
                        help='Periodicity of checking in seconds '
                             '(default: 21600)')
    args = parser.parse_args()
    return args


def main():
    """
    Run bot
    """
    # Parsing command line arguments
    args = parse_command_line_arguments()
    # Connection to Telegram
    token = args.token
    data_base_path = args.database
    periodicity = args.periodicity
    updater = Updater(token)
    # Create logic object
    logic = MonitorBotLogic(data_base_path)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Register handlers
    dp.add_handler(CommandHandler("start", logic.start))
    dp.add_handler(CommandHandler("help", logic.help))
    dp.add_handler(CommandHandler("show", logic.show))
    dp.add_handler(CommandHandler("add", logic.add, pass_args=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("delete", logic.delete, pass_args=True))
    dp.add_handler(CallbackQueryHandler(logic.choice, pass_chat_data=True))
    # Run periodic refreshes according to periodicity
    updater.job_queue.run_repeating(logic.refresh, periodicity)
    # Start the bot
    updater.start_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
