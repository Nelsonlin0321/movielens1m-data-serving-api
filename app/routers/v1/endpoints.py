# pylint: disable=duplicate-code

from fastapi import APIRouter, HTTPException

from .dynamodb_engine import DynamoBD
from .mongodb_engine import MongoDB
from .utils import get_version, logger

version = get_version(__name__)

router = APIRouter(
    prefix=f"/{version}/movies",
    responses={404: {"description": "Not found"}},
    tags=[version],
)

dynamodb = DynamoBD(
    table_name="movielens_movie"
)

mongodb = MongoDB(db_name="movielens1m", collection_name="movie")


@router.get("/")
async def get_movie_by_genre(genre: str = None,
                             page_size: int = 12,
                             order_by: str = "release_year",
                             movie_id: int = None):
    # pylint:disable=unused-argument,broad-exception-caught,unexpected-keyword-arg
    try:
        response = dynamodb.get_movies(
            genre=genre, page_size=page_size, order_by=order_by, movie_id=movie_id)
    except Exception as exception:
        logger.error(exception)
        return HTTPException(status_code=500, detail=str(exception))
    return response


@router.get("/search")
async def search_movie(q: str, limit: int = 30):
    try:
        response = mongodb.search(
            query=q, limit=limit, index='default', search_field='title',)
    # pylint:disable=unused-argument,broad-exception-caught,unexpected-keyword-arg
    except Exception as exception:
        logger.error(exception)
        return HTTPException(status_code=500, detail=str(exception))
    return response
