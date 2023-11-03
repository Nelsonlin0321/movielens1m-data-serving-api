import os
from typing import List
from pymongo import MongoClient

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise Exception("MONGODB_URL is not defined")


class MongoDB():
    def __init__(self, db_name="movielens1m", collection_name="movie") -> None:
        self.client = MongoClient(MONGODB_URL)
        self.db_name = db_name
        self.collection_name = collection_name

    def search(self, query, index='default', search_field='title', limit=30) -> List:

        results = self.client[self.db_name][self.collection_name].aggregate([

            {

                '$search': {

                    'index': index,

                    'text': {

                        'query': query,

                        'path': search_field,

                        "fuzzy": {
                            "maxEdits": 2,
                            "maxExpansions": 50,
                        }

                    }

                }

            },

            {

                '$limit': limit

            },

            {

                '$project': {

                    '_id': 0,
                }

            }

        ])

        results = list(results)

        response = {}
        response['results'] = results
        response['count'] = len(results)

        return response
