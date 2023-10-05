# pylint: disable=duplicate-code

from fastapi import APIRouter, HTTPException, Request

from ...dynamodb_engine import Movie
from ...utils import get_version, logger

version = get_version(__name__)

router = APIRouter(
    prefix=f"/{version}/movies",
    responses={404: {"description": "Not found"}},
    tags=[version],
)

movie_table = Movie(
    table_name="movielens_movie"
)


@router.get("/")
async def get_celebrity_series_list(genre: str, request: Request):
    # pylint:disable=unused-argument,broad-exception-caught
    try:
        response = movie_table.get_movies(genre=genre)
    except Exception as exception:
        logger.error(exception)
        return HTTPException(status_code=500, detail=str(exception))
    return response
