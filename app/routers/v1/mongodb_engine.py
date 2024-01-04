import os
from dataclasses import dataclass
from typing import Dict

from pymongo import MongoClient

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL is not defined")


@dataclass
class SearchParameters:
    search_text:  str
    genre: str
    skip: int
    order_by: str
    limit: int = 30


class MongoDB():
    def __init__(self, db_name="movielens1m", collection_name="movie") -> None:
        self.client = MongoClient(MONGODB_URL)
        self.db_name = db_name
        self.collection_name = collection_name

    def search(self, params: SearchParameters) -> Dict:
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
                            'maxExpansions': 10
                        }
                    }
                }
            }

            aggregate_pipeline.append(search_stage)

            aggregate_pipeline.append({
                '$addFields': {
                    'relevance': {"$meta": "searchScore"}
                }
            },)

        if params.genre:
            genre_filter_stage = {
                '$match': {
                    'genres': params.genre
                }
            }
            aggregate_pipeline.append(genre_filter_stage)

        order_condition_1 = params.order_by in ["rating", "release_year"]
        order_condition_2 = params.order_by == 'relevance' and params.search_text
        if order_condition_1 or order_condition_2:
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

        print(aggregate_pipeline)

        results = self.client[self.db_name][self.collection_name].aggregate(
            aggregate_pipeline)

        results = list(results)

        response = {}
        response['results'] = results
        response['count'] = len(results)

        return response
