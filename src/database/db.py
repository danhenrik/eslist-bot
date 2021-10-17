from pymongo import MongoClient
from env import MONGO_DB_URL
import ssl

class DatabaseException(Exception):
    pass


cluster = MongoClient(MONGO_DB_URL,ssl_cert_reqs=ssl.CERT_NONE)
db = cluster['ESList-bot']

# Creates or get the 2 collections from the cluster.
events = db.events
subscriptions = db.subscriptions
