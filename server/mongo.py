import os

from pymongo import MongoClient

client = MongoClient(os.environ["MONGO_CONNECTION_STRING"])
DB = "hat"


def upload(payload, name):
    client[DB][f"{name}s"].insert_one(payload)
