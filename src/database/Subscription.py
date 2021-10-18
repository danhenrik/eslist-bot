import datetime
from database.db import subscriptions, DatabaseException


class Subscription:
    def __init__(self, subscriber_name, subscriber_id, event_id, subscribed_at=0, id=0):
        self.Name = subscriber_name
        self.SubscriberID = subscriber_id
        self.EventID = event_id
        if not subscribed_at:
            self.SubscribedAt = datetime.datetime.utcnow()
        else:
            self.SubscribedAt = subscribed_at
        self.ID = id

    # Saves the local instance of the subscription to the database
    def save(self):
        if not self.ID:
            if SubscriptionService.find_by_event_id(self.EventID, self.SubscriberID):
                raise DatabaseException(
                    "You're already subscribed to this event")
            self.ID = subscriptions.insert_one(
                {"name": self.Name, "subscriber_id": self.SubscriberID, "event_id": self.EventID,
                 "subscribed_at": self.SubscribedAt}).inserted_id

    # Synchronizes the current instance with the database data
    def sync(self):
        if self.ID:
            res = subscriptions.find_one({"_id": self.ID})
            if res:
                self.Name = res.name
                self.SubscriberID = res.subscriber_id
                self.EventID = res.event_id
                self.SubscribedAt = res.subscribed_at

    # Update's the current subscription in the database
    def update(self):
        if self.ID:
            subscriptions.update_one({"_id": self.ID}, {"name": self.Name})

    # Deletes the event in the database
    def delete(self):
        subscriptions.delete_one({"_id": self.ID})


class SubscriptionService:
    @staticmethod
    def find_by_event_id(event_id, sub_id):
        res = subscriptions.find_one(
            {'event_id': event_id, 'subscriber_id': sub_id})
        if res:
            return Subscription(res['name'], res['subscriber_id'], res['event_id'], res['subscribed_at'], res['_id'])
        return
