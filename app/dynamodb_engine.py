import logging
from decimal import Decimal
from typing import Dict, List

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

dynamodb = boto3.resource("dynamodb")


def remove_decimals(item: Dict) -> Dict:
    for key, value in item.items():
        if isinstance(value, Decimal):
            if value % 1 == 0:
                item[key] = int(value)
            else:
                item[key] = round(float(value), 4)
    return item


class Movie:
    def __init__(self, table_name: str = "movielens_movie",
                 global_secondary_index: str = "rank_index") -> None:
        self.table_name = table_name
        self.table = dynamodb.Table(table_name)
        self.global_secondary_index = global_secondary_index

    def get_movies(self, genre: str) -> List:
        # pylint:disable=no-else-raise,line-too-long
        try:

            if genre != 'all':
                response = self.table.query(
                    KeyConditionExpression=Key("genre").eq(genre)
                )
            else:
                response = self.table.query(
                    IndexName=self.global_secondary_index,
                    KeyConditionExpression=Key("rank").eq(1)
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
            items = response.get("Items", [])
            if items:
                items = [remove_decimals(item) for item in items]
            return items
