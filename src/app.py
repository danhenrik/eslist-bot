from pymongo import response
from telegram.ext import CommandHandler, Updater
from env import TOKEN
from actions import say, give_feedback
from database.db import DatabaseException
from database.Event import Event, EventService
from database.Subscription import Subscription, SubscriptionService

# TODO
# Possible future features
# Command /myEvents tho show my subscribed events
# Event description
# Event deadlines
# At user update update the name on the list
# At /in add an optional argument between "" with the personalized name
# Command /clear to clear event subscription list

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
                              " groups, my mission is to organize subscriptions lists in a better way reducing message flooding."))
    else:
        say(update, context, ("I'm already listening (only to commands), send /help for more information about the commands."))


def getHelp(update, context):
    if not isPrivate(update):
        say(update, context, "Commands:\n" +
            "/create <b>event-name</b> : Creates a new event\n" +
            "/delete <b>event-name</b> : Delete the event\n" +
            "/list <b>event-name</b> : List the subscribers names of the event\n" +
            "/events : List all the registered events\n" +
            "/in <b>event-name</b>: Subscribes you to a event\n" +
            "/out <b>event-name</b> : Unsubscribe you from the event\n" +
            "/feedback <b>your-message</b> : Send me a feedback if you found some bug or something that can be improved (Private only)\n")
    else:
        say(update, context,  "Commands:\n" +
            "/create <b>event-name</b> : Creates a new event (Groups only)\n" +
            "/delete <b>event-name</b> : Delete the event (Groups only)\n" +
            "/list <b>event-name</b> : List the subscribers names of the event (Groups only)\n" +
            "/events : List all the registered events (Groups only)\n" +
            "/in <b>event-name</b>: Subscribes you to a event (Groups only)\n" +
            "/out <b>event-name</b> : Unsubscribe you from the event (Groups only)\n" +
            "/feedback <b>your-message</b> : Send me a feedback if you found some bug or something that can be improved")


def create(update, context):
    try:
        if isPrivate(update):
            say(update, context, 'This command only works in groups')
            return
        args = extractArgs(update)
        if not args:
            say(update, context, 'You need to tell me a name for the event', True)
            return
        chatID = update.message.chat.id
        creatorID = update.message.from_user.id
        event = Event(args, chatID, creatorID)
        event.save()
        say(update, context, '<b>' + event.Name + '</b> succesfully created')
    except DatabaseException as error:
        say(update, context, error.args[0])


def delete(update, context):
    if isPrivate(update):
        say(update, context, 'This command only works in groups')
        return
    args = extractArgs(update)
    if not args:
        say(update, context, 'You need to tell me the name of the event', True)
        return
    chatID = update.message.chat.id
    event = EventService.find_by_name(args, chatID)
    if not event:
        say(update, context, "There's no event registered with the given name", True)
        return
    creatorID = update.message.from_user.id
    if event.CreatorID == creatorID:
        event.delete()
        say(update, context, '<b>' + event.Name + '</b> succesfully deleted!')
    else:
        say(update, context, 'You need to be the event creator to delete it', True)


def events(update, context):
    if isPrivate(update):
        say(update, context, 'This command only works in groups')
        return
    chatID = update.message.chat.id
    events = EventService.find_by_chat_id(chatID)
    if not events:
        say(update, context, "There's no events registered yet", True)
        return
    response_message = 'Registered events:\n'
    for i in range(0, len(events)):
        response_message = response_message + \
            str(i+1) + ' - ' + events[i].Name + '\n'
    say(update, context, response_message)


def subscribe(update, context):
    try:
        if isPrivate(update):
            say(update, context, 'This command only works in groups')
            return
        args = extractArgs(update)
        if not args:
            say(update, context, 'You need to tell me the name of the event', True)
            return
        chatID = update.message.chat.id
        event = EventService.find_by_name(args, chatID)
        if not event:
            say(update, context, "There's no events with the given name", True)
            return
        subscriberID = update.message.from_user.id
        subscriberName = update.message.from_user.name
        sub = Subscription(subscriberName, subscriberID, event.ID)
        sub.save()
        say(update, context, 'Successfully subscribed to <b>' +
            event.Name + '</b>', True)
    except DatabaseException as error:
        say(update, context, error.args[0])


def unsubscribe(update, context):
    if isPrivate(update):
        say(update, context, 'This command only works in groups')
        return
    args = extractArgs(update)
    if not args:
        say(update, context, 'You need to tell me the name of the event', True)
        return
    chatID = update.message.chat.id
    event = EventService.find_by_name(args, chatID)
    if not event:
        say(update, context, "There's no events with the given name")
        return
    subscriberID = update.message.from_user.id
    subscription = SubscriptionService.find_by_event_id(event.ID, subscriberID)
    if not subscription:
        say(update, context, "You're not subscribed to this event", True)
        return
    subscription.delete()
    say(update, context, 'Successfully unsubscribed from <b>' +
        event.Name + '</b>', True)


def list_sub(update, context):
    if isPrivate(update):
        say(update, context, 'This command only works in groups')
        return
    args = extractArgs(update)
    if not args:
        say(update, context, 'You need to tell me the name of the event', True)
        return
    chatID = update.message.chat.id
    event = EventService.find_by_name(args, chatID)
    if not event:
        say(update, context, "There's no events with the given name")
        return
    subs = event.get_subs()
    if not subs:
        say(update, context, "There's no subscriptions to this event yet")
        return
    response_message = '<b>' + event.Name + '</b> subscribers:\n'
    for i in range(0, len(subs)):
        response_message = response_message + \
            str(i+1) + ' - <b>' + subs[i].Name + '</b>\n'
    say(update, context, response_message, True)


def feedback(update, context):
    if not isPrivate(update):
        say(update, context,
            "If you want to send me a feedback please do so on my private")
        return
    message = extractArgs(update)
    sender = update.message.from_user
    give_feedback(context, message, sender)
    say(update, context, "Thank you for your feedback 😄\n")


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("create", create))
    dispatcher.add_handler(CommandHandler("delete", delete))
    dispatcher.add_handler(CommandHandler("events", events))
    dispatcher.add_handler(CommandHandler("in", subscribe))
    dispatcher.add_handler(CommandHandler("out", unsubscribe))
    dispatcher.add_handler(CommandHandler("list", list_sub))
    dispatcher.add_handler(CommandHandler("feedback", feedback))
    dispatcher.add_handler(CommandHandler("help", getHelp))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
