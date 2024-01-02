import os
from dataclasses import dataclass
from typing import List, Optional

from pymongo import MongoClient

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL is not defined")


@dataclass
class SearchParameters:
    search_text:  Optional[str] = None
    genre: Optional[str] = None
    skip: Optional[int] = None
    order_by: str = 'release_year'
    limit:  Optional[int] = 30


class MongoDB():
    def __init__(self, db_name="movielens1m", collection_name="movie") -> None:
        self.client = MongoClient(MONGODB_URL)
        self.db_name = db_name
        self.collection_name = collection_name

    def search(self, params: SearchParameters) -> List:
        aggregate_pipeline = []

        if params.search_text:
            search_stage = {
                '$search': {
                    'index': 'default',
                    'text': {
                        'query': params.search_text,
                        'path': 'title',
                        'fuzzy': {
                            'maxEdits': 2,
                            'maxExpansions': 50
                        }
                    }
                }
            }

            aggregate_pipeline.append(search_stage)

        if params.genre:
            genre_filter_stage = {
                '$match': {
                    'genres': params.genre
                }
            }

            aggregate_pipeline.append(genre_filter_stage)

        if params.order_by:
            sort_stage = {
                '$sort': {
                    params.order_by: -1
                }
            }
            aggregate_pipeline.append(sort_stage)

        aggregate_pipeline.append({
            '$project': {
                '_id': 0
            }
        })
        if params.skip:
            aggregate_pipeline.append({
                "$skip": params.skip
            })

        if params.limit:
            aggregate_pipeline.append({
                "$limit": params.limit
            })

        results = self.client[self.db_name][self.collection_name].aggregate(
            aggregate_pipeline)

        results = list(results)

        response = {}
        response['results'] = results
        response['count'] = len(results)

        return response
