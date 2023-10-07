import logging
from typing import Dict, List

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

dynamodb = boto3.resource("dynamodb")


class Movie:
    def __init__(self, table_name: str = "movielens_movie") -> None:
        self.table_name = table_name
        self.table = dynamodb.Table(table_name)

    def get_movies(self, genre: str,
                   page_size: int = 12,
                   order_by: str = "release_year") -> List[Dict]:
        # pylint:disable=no-else-raise,line-too-long
        if not order_by:
            order_by = "release_year"

        order_by = order_by.replace("_", "-")

        try:
            if genre:
                index_name = f"genre-{order_by}-index"
                response = self.table.query(
                    IndexName=index_name,
                    KeyConditionExpression=Key("genre").eq(genre),
                    Limit=page_size,
                    ScanIndexForward=False
                )
            else:
                index_name = f"rank-{order_by}-index"
                response = self.table.query(
                    IndexName=index_name,
                    KeyConditionExpression=Key("rank").eq(1),
                    Limit=page_size,
                    ScanIndexForward=False
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
