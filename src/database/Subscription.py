import datetime
from database.db import subscriptions


class Subscription:
    def __init__(self, subscriber_name, subscriber_id, event_id):
        self.Name = subscriber_name
        self.SubscriberID = subscriber_id
        self.EventID = event_id
        self.SubscribedAt = datetime.datetime.utcnow()
        self.ID = 0

    # Saves the local instance of the subscription to the database
    def save(self):
        if not self.iD:
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
    def find_by_id(sub_id):
        return subscriptions.find_one({"_id": sub_id})

    @staticmethod
    def find_all():
        return subscriptions.find()
