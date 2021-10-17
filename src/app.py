from pymongo import response
from telegram.ext import CommandHandler, Updater
from env import TOKEN
from actions import say
from database.db import DatabaseException
from database.Event import Event, EventService


# Return if the current context of the message is in private
def isPrivate(update):
    return update.message.chat.type == "private"


# Extracts the arguments from the command input
def extractArgs(update):
    arr = update.message.text.split(" ")
    if len(arr) >= 2:
        arg = ''
        for i in range(1, len(arr)):
            arg = arg + arr[i] + ' '
        return arg
    else:
        return


def start(update, context):
    if isPrivate(update):
        say(update, context, ("Hello!\n I'm the Event Subscriptions List bot, all i do is manage event subscriptions list in" +
                              " groups, my mission is to organize subscriptions lists in a better way avoiding message flooding."))
    else:
        say(update, context, ("I'm already listening (only commands), send /help for more information about the commands."))


def getHelp(update, context):
    response_message = "Commands:\n" +\
        "/create <event-name> : Creates a new event\n" + \
        "/in <event-name> : Subscribes to a created event\n" +\
        "/out <event-name> : Unsubscribe yourself from the event\n" +\
        "/delete <event-name> : Delete the event\n" +\
        "/list <event-name> : List the subscribers names\n" +\
        "/events : List all the registered events in the current group\n" +\
        "/feedback <your-message> : Send me a feedback if you found some bug or something that may be improved (Private)\n"
    if not isPrivate(update):
        say(update, context, response_message)
    else:
        response_message = response_message + \
            "\nThose commands will only work in groups!\n"
        say(update, context, response_message)


def create(update, context):
    try:
        if isPrivate(update):
            say(update, context, 'This command only works for groups')
            return
        args = extractArgs(update)
        if args:
            chatID = update.message.chat.id
            creatorID = update.message.from_user.id
            event = Event(args, chatID, creatorID)
            event.save()
            say(update, context, 'Event succesfully created!')
        else:
            say(update, context, 'You need to tell me a name for the event')
    except DatabaseException as error:
        say(update, context, error.args[0])


def delete(update, context):
    if isPrivate(update):
        say(update, context, 'This command only works for groups')
        return
    args = extractArgs(update)
    if args:
        chatID = update.message.chat.id
        creatorID = update.message.from_user.id
        event = EventService.find_by_name(args, chatID)
        if event.CreatorID == creatorID:
            event.delete()
            say(update, context, 'Event succesfully deleted!')
        else:
            say(update, context, 'You need to be the event creator to delete it')
    else:
        say(update, context, 'You need to tell me the name of the event')


def events(update, context):
    if isPrivate(update):
        say(update, context, 'This command only works for groups')
        return
    chatID = update.message.chat.id
    events = EventService.find_by_chat_id(chatID)
    if events:
        response_message = 'Registered events:\n'
        for i in range(0, len(events)):
            response_message = response_message + \
                str(i+1) + ' - '+ events[i].Name + '\n'
        say(update, context, response_message)
    else:
        say(update, context, "There's no event registered yet!")


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("create", create))
    dispatcher.add_handler(CommandHandler("delete", delete))
    dispatcher.add_handler(CommandHandler("events", events))
    dispatcher.add_handler(CommandHandler("in", start))
    dispatcher.add_handler(CommandHandler("out", start))
    dispatcher.add_handler(CommandHandler("help", getHelp))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
