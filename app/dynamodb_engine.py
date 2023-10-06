import logging
from typing import List, Dict

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

dynamodb = boto3.resource("dynamodb")


class Movie:
    def __init__(self, table_name: str = "movielens_movie",
                 global_secondary_index: str = "rank_index") -> None:
        self.table_name = table_name
        self.table = dynamodb.Table(table_name)
        self.global_secondary_index = global_secondary_index

    def get_movies(self, genre: str, page_size=12) -> List[Dict]:
        # pylint:disable=no-else-raise,line-too-long
        try:
            if genre:
                response = self.table.query(
                    KeyConditionExpression=Key("genre").eq(genre),
                    Limit=page_size
                )
            else:
                response = self.table.query(
                    IndexName=self.global_secondary_index,
                    KeyConditionExpression=Key("rank").eq(1),
                    Limit=page_size
                )

        except ClientError as err:
            status_code = err.response["Error"]["Code"]
            message = err.response["Error"]["Message"]
            logger.error(
                "Could not get %s movies from table %s. Here's why: %s: %s",
                genre,
                self.table_name,
                status_code,
                message,
            )
            raise
        else:
            response_dict = {}
            response_dict['results'] = response.get("Items", [])
            response_dict['count'] = response.get("Count", 0)
            response_dict['last_evaluated_key'] = response.get(
                "LastEvaluatedKey", {})
            return response_dict
