from telegram.ext import DictPersistence
from env import DEV_ID
from datetime import datetime

persistence = DictPersistence(
    store_bot_data=False, store_chat_data=True, store_user_data=False)


def say(update, context, message, delete=0):
    if delete:
        delMessage = persistence.get_chat_data(
        )[update.effective_chat.id]
        if delMessage:
            # Deletes the last message
            context.bot.delete_message(
                update.effective_chat.id, delMessage['message_id'])
    res = context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, parse_mode='HTML')
    # Thosse two ifs are here just so the output comes out after the last message was deleted, if we didn't 
    # separate in two the message would come in before the past goes out.
    if delete:
        # Place the current message as the next one
        persistence.update_chat_data(update.effective_chat.id, {
                                     "message_id": res.message_id})


def give_feedback(context, message, sender):
    now = datetime.now()
    date_time = now.strftime("%d-%b-%Y [%H:%M:%S]")
    message = 'Feedback sent at ' + date_time + ' by <a href="tg://user?id=' + \
        str(sender.id) + '">' + sender.name + '</a>\nMessage:\n' + message
    context.bot.send_message(chat_id=DEV_ID, text=message, parse_mode='HTML')
