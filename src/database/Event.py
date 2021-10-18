import datetime
from database.db import events, subscriptions, DatabaseException
from database.Subscription import Subscription


class Event:
    def __init__(self, name, chat_id, creator_id, created_at=0, id=0):
        self.Name = name
        self.ChatID = chat_id
        self.CreatorID = creator_id
        if not created_at:
            self.createdAt = datetime.datetime.utcnow()
        else:
            self.createdAt = created_at
        self.ID = id

    # Saves the local instance of the event to the database
    def save(self):
        if not self.ID:
            if EventService.find_by_name(self.Name, self.ChatID):
                raise DatabaseException(
                    "The name you've passed is already registered.")
            self.ID = events.insert_one({"name": self.Name, "chat_id": self.ChatID, "creator_id": self.CreatorID,
                                         "created_at": self.createdAt}).inserted_id

    # Synchronizes the current instance with the database data
    def sync(self):
        res = events.find_one({"_id": self.ID})
        if res:
            self.Name = res.name
            self.ChatID = res.chat_id
            self.CreatorID = res.creator_id
            self.createdAt = res.created_at

    # Update's the current subscription in the database
    def update(self):
        if self.ID:
            events.update_one({"_id": self.ID}, {"name": self.Name})

    # Deletes the event in the database
    def delete(self):
        if self.ID:
            subs = self.get_subs()
            for sub in subs:
                sub.delete()
            events.delete_one({"_id": self.ID})

    # Query's all the subscribers to the current event.
    def get_subs(self):
        if self.ID:
            subs = subscriptions.find({"event_id": self.ID})
            if subs:
                res = []
                for sub in subs:
                    res.append(Subscription(
                        sub['name'], sub['subscriber_id'], sub['event_id'], sub['subscribed_at'], sub['_id']))
            return res
        return []


class EventService:
    @ staticmethod
    def find_by_id(event_id):
        res = events.find_one({"_id": event_id})
        if res:
            return Event(res['name'], res['chat_id'], res['creator_id'], res['created_at'], res['_id'])
        else:
            return

    @ staticmethod
    def find_by_name(name, chat_id):
        res = events.find_one({"name": name, "chat_id": chat_id})
        if res:
            return Event(res['name'], res['chat_id'], res['creator_id'], res['created_at'], res['_id'])
        else:
            return

    @ staticmethod
    def find_by_chat_id(chat_id):
        res = events.find({"chat_id": chat_id})
        finalResponse = []
        if res:
            for event in res:
                finalResponse.append(Event(
                    event['name'], event['chat_id'], event['creator_id'], event['created_at'], event['_id']))
        return finalResponse
